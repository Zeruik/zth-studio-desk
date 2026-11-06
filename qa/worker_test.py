"""Synthetic-only regression tests. No real GitHub or DNS writes/requests."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'python'))
import base64
import copy
import hashlib
import json
import os
import socket
import subprocess
import tempfile
import unittest
import urllib.error
import zipfile
from unittest.mock import patch
import worker
from validation import DeskError, validate, link, domain
from sitegen import generate
from github_pages import deploy, GitHub, MARKER, owner_marker


def fixture():
    return {'format': 'zth-desk-project', 'schema': 1, 'producer': '1.0.0', 'id': 'demoProject', 'name': 'PRIVATE_PROJECT_NAME', 'updatedAt': '2026-11-06T00:00:00Z', 'settings': {'language': 'zh', 'theme': 'warm', 'autoBuild': False}, 'operations': {'tasks': [{'id': 'taskOne', 'title': 'PRIVATE_TASK', 'owner': 'PRIVATE_OWNER', 'due': '2026-11-08', 'status': 'doing', 'channel': 'event', 'notes': 'PRIVATE_NOTES'}], 'drafts': [{'id': 'draftOne', 'title': 'PRIVATE_DRAFT', 'body': 'PRIVATE_BODY', 'tags': ['PRIVATE_TAG'], 'updatedAt': '2026-11-06T00:00:00Z'}]}, 'site': {'title': '公开工作室 / Public studio', 'description': '设计与制作 / Design and making', 'language': 'zh-CN', 'theme': 'studio', 'accent': '#16806a', 'domain': '', 'basePath': '', 'assets': [], 'pages': [{'id': 'homePage', 'slug': 'index', 'title': '一起做好作品', 'nav': True, 'sections': [{'id': 'heroOne', 'type': 'hero', 'title': 'Studio', 'body': 'Plain text\n\nSecond paragraph', 'image': '', 'items': [], 'link': 'about.html#aboutText', 'label': 'About'}]}, {'id': 'aboutPage', 'slug': 'about', 'title': '关于', 'nav': True, 'sections': [{'id': 'aboutText', 'type': 'text', 'title': 'About', 'body': 'A public section', 'image': '', 'items': [], 'link': '', 'label': ''}]}]}}


class FakeGitHub:
    def __init__(self, project_id='demoProject', existing=True, foreign=False, drift=False, pages_foreign=False, fail_pages=False, built=False):
        self.calls, self.blobs = [], []
        self.existing, self.foreign, self.drift = existing, foreign, drift
        self.pages_foreign, self.fail_pages, self.built = pages_foreign, fail_pages, built
        self.project_id, self.ref_reads = project_id, 0
        self.pages_created = existing
        self.old, self.new = 'a' * 40, 'c' * 40
    def request(self, method, path, data=None, missing=False):
        self.calls.append((method, path, copy.deepcopy(data)))
        if path == '/user':
            return {'login': 'synthetic-user', 'id': 1234, 'name': 'PRIVATE_REAL_NAME'}
        if path == '/repos/owner/site':
            return {'default_branch': 'main'}
        if path.endswith('/git/ref/heads/main'):
            return {'object': {'sha': 'd' * 40}}
        if path.endswith('/git/ref/heads/zth-site'):
            self.ref_reads += 1
            if not self.existing:
                return None
            return {'object': {'sha': 'b' * 40 if self.drift and self.ref_reads > 1 else self.old}}
        if '/contents/' in path:
            if self.foreign:
                return None
            mark = owner_marker(self.project_id)
            return {'encoding': 'base64', 'size': 150, 'content': base64.b64encode(json.dumps(mark).encode()).decode()}
        if path.endswith('/git/blobs'):
            self.blobs.append(base64.b64decode(data['content']))
            return {'sha': 'e' * 40}
        if path.endswith('/git/trees'):
            return {'sha': 'f' * 40}
        if path.endswith('/git/commits'):
            return {'sha': self.new}
        if path.endswith('/pages/builds/latest'):
            return {'commit': self.new if self.built else self.old, 'status': 'built'}
        if path.endswith('/pages'):
            if method != 'GET' and self.fail_pages:
                raise DeskError('GITHUB_PERMISSION', 'Synthetic failure')
            if self.pages_foreign:
                return {'source': {'branch': 'main', 'path': '/'}}
            if method == 'POST':
                self.pages_created = True
            if not self.pages_created and method == 'GET':
                return None
            return {'source': {'branch': 'zth-site', 'path': '/'}, 'https_certificate': {'state': 'approved'}}
        if method in ('PATCH', 'POST') and '/git/refs' in path:
            return {}
        raise AssertionError((method, path))


class WorkerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='zth-desk-test-')
        self.base = Path(self.temp.name)
        self.number = 0
    def tearDown(self):
        self.temp.cleanup()
    def output(self):
        self.number += 1
        result = self.base / ('job' + str(self.number))
        result.mkdir()
        return str(result)
    def run_job(self, task, project=None, options=None, client=None):
        return worker.handle({'task': task, 'project': project or fixture(), 'options': options or {}, 'outputDir': self.output()}, github_client=client)
    def test_three_themes_and_public_boundary(self):
        for theme in ('studio', 'editorial', 'portfolio'):
            p = fixture()
            p['site']['theme'] = theme
            p['site']['pages'][0]['sections'][0]['body'] = '<script>alert(1)</script> & "quoted"'
            result = self.run_job('build', p)
            with zipfile.ZipFile(result['zipPath']) as archive:
                self.assertIsNone(archive.testzip())
                names = archive.namelist()
                self.assertIn('index.html', names)
                self.assertIn('about.html', names)
                for name in names:
                    body = archive.read(name)
                    self.assertNotIn(b'PRIVATE_', body)
                    self.assertNotIn(b'<script>', body)
                html = archive.read('index.html').decode()
                self.assertIn('&lt;script&gt;', html)
                self.assertIn('./assets/site.css', html)
                self.assertIn('theme-' + theme, html)
                self.assertIn('<h1>Studio</h1>', html)
                self.assertEqual(html.count('id="heroOne"'), 1)
                self.assertNotIn('<h1>一起做好作品</h1>', html)
                self.assertEqual(html.count('&lt;script&gt;'), 1)
                manifest = json.loads(archive.read('site-manifest.json'))
                for entry in manifest['files']:
                    self.assertEqual(hashlib.sha256(archive.read(entry['path'])).hexdigest(), entry['sha256'])
            self.assertIn('<style>', result['previewHtml'])
            self.assertEqual(result['report']['errors'], [])
    def test_backup_is_complete_and_separate(self):
        result = self.run_job('backup')
        self.assertEqual(json.loads(Path(result['path']).read_text(encoding='utf-8')), validate(fixture()))
        self.assertFalse(result['encrypted'])
        self.assertTrue(result['private'])
    def test_calendar_escaping_dates_folding_and_drafts(self):
        p = fixture()
        p['operations']['tasks'][0]['title'] = '中文' * 50 + '\nBEGIN:VEVENT,;'
        result = self.run_job('calendar', p)
        raw = Path(result['path']).read_bytes()
        self.assertIn(b'DTSTART;VALUE=DATE:20261108', raw)
        self.assertIn(b'DTEND;VALUE=DATE:20261109', raw)
        self.assertEqual(raw.count(b'\r\nBEGIN:VEVENT\r\n'), 1)
        for line in raw.split(b'\r\n'):
            self.assertLessEqual(len(line), 75)
            line.decode('utf-8')
        draft = self.run_job('drafts')
        self.assertIn('PRIVATE_BODY', Path(draft['path']).read_text(encoding='utf-8'))
    def test_link_and_asset_audit(self):
        p = fixture()
        p['site']['pages'][0]['sections'][0]['link'] = 'about.html#missing'
        result = self.run_job('audit', p)
        self.assertEqual(result['report']['errors'][0]['code'], 'BROKEN_LINK')
        for value in ['javascript:alert(1)', 'data:text/html,x', '../index.html', 'https://safe.example/%0aBad', 'https://user:pw@safe.example', 'file:///secret']:
            with self.assertRaises(DeskError):
                link(value)
        self.assertEqual(domain('例子.中国'), 'xn--fsqu00a.xn--fiqs8s')
    def test_image_signatures_and_only_used_assets(self):
        p = fixture()
        # Tiny real PNG; no filesystem image imports.
        png = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/l1sAAAAASUVORK5CYII='
        p['site']['assets'] = [{'id': 'imageOne', 'name': 'PRIVATE_FILENAME.png', 'mime': 'image/png', 'data': png, 'alt': 'A pixel'}, {'id': 'unusedImage', 'name': 'unused.png', 'mime': 'image/png', 'data': png, 'alt': ''}]
        p['site']['pages'][0]['sections'][0]['image'] = 'imageOne'
        result = self.run_job('build', p)
        names = [x['path'] for x in result['files']]
        self.assertEqual(sum(n.endswith('.png') for n in names), 1)
        self.assertIn('data:image/png;base64,', result['previewHtml'])
        self.assertNotIn('PRIVATE_FILENAME', result['previewHtml'])
        p['site']['assets'][0]['mime'] = 'image/jpeg'
        with self.assertRaises(DeskError):
            validate(p)
    def test_validation_and_output_boundaries(self):
        for mutate in [lambda p: p.update(schema=2), lambda p: p['site'].update(secret='x'), lambda p: p['site']['pages'][0].update(slug='../secret'), lambda p: p['operations']['tasks'][0].update(due='2026-02-30')]:
            p = fixture()
            mutate(p)
            with self.assertRaises(DeskError):
                validate(p)
        with self.assertRaises(DeskError):
            worker.parse(b'{"a":1,"a":2}')
        with self.assertRaises(DeskError):
            worker.Output('../outside')
        out = worker.Output(self.output())
        for name in ['../x', '/x', 'a/../../x', 'a\\x', 'C:/x', 'x:stream']:
            with self.assertRaises(DeskError):
                out.write(name, b'x')
        out.write('one.txt', b'preserve')
        with self.assertRaises(DeskError):
            worker.Output(str(out.root))
        for reserved in ('CON', 'nul', 'COM1', 'Lpt9'):
            p = fixture()
            p['id'] = reserved
            with self.assertRaises(DeskError):
                validate(p)
        p = fixture()
        p['producer'] = '1.0.2'
        self.assertEqual(validate(p)['producer'], '1.0.2')
    def test_fixed_api_host_redirect_refusal_and_redacted_http_error(self):
        api = GitHub('SYNTHETIC_SECRET_TOKEN')
        class Opener:
            def __init__(self):
                self.request = None
            def open(self, request, timeout):
                self.request = request
                raise urllib.error.HTTPError(request.full_url, 302, 'SYNTHETIC_SECRET_TOKEN', {'Location': 'https://untrusted.example/'}, None)
        fake = Opener()
        api.opener = fake
        with self.assertRaises(DeskError) as caught:
            api.request('GET', '/repos/owner/site')
        self.assertEqual(fake.request.full_url, 'https://api.github.com/repos/owner/site')
        self.assertNotIn('SYNTHETIC_SECRET_TOKEN', caught.exception.message)
        self.assertEqual(caught.exception.code, 'GITHUB_HTTP')
        for url in ['https://untrusted.example/', '//untrusted.example/', '/repos/owner/../other']:
            with self.assertRaises(DeskError):
                api.request('GET', url)
    def test_invalid_confirmation_and_empty_repo_have_no_mutations(self):
        api = FakeGitHub()
        with self.assertRaises(DeskError):
            self.run_job('deploy', options={**self.options(), 'confirmPublic': False}, client=api)
        self.assertEqual(api.calls, [])
        class Empty(FakeGitHub):
            def request(self, method, path, data=None, missing=False):
                if path.endswith('/git/ref/heads/main'):
                    self.calls.append((method, path, data))
                    return None
                return super().request(method, path, data, missing)
        api = Empty()
        with self.assertRaises(DeskError) as caught:
            self.run_job('deploy', options=self.options(), client=api)
        self.assertEqual(caught.exception.code, 'REPOSITORY_INITIALIZE')
        self.assertTrue(all(method == 'GET' for method, _, _ in api.calls))
    def test_dns_observation_is_not_ownership_or_tls(self):
        site = fixture()['site']
        site['domain'] = 'example.com'
        resolver = lambda *a, **k: [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('185.199.108.153', 443))]
        result = worker.dns_check(site, resolver)
        self.assertTrue(result['matchesGithubPagesAddress'])
        self.assertFalse(result['ownershipVerified'])
        self.assertFalse(result['tlsVerified'])
    def options(self):
        return {'owner': 'owner', 'repo': 'site', 'token': 'SYNTHETIC_SECRET_TOKEN', 'confirmPublic': True}
    def test_github_owned_update_nonforce_no_private_data_or_realname(self):
        api = FakeGitHub()
        result = self.run_job('deploy', options=self.options(), client=api)
        self.assertTrue(result['uploaded'])
        self.assertEqual(result['pagesStatus'], 'pending')
        self.assertFalse(result['live'])
        self.assertTrue(any(method == 'PATCH' and data.get('force') is False for method, _, data in api.calls if data))
        for method, path, data in api.calls:
            if method != 'GET':
                self.assertNotIn('/heads/main', path)
        raw = b'\n'.join(api.blobs)
        self.assertNotIn(b'PRIVATE_', raw)
        self.assertNotIn(b'demoProject', raw)
        commit = next(data for method, path, data in api.calls if path.endswith('/git/commits'))
        self.assertEqual(commit['author']['name'], 'synthetic-user')
        self.assertEqual(commit['author']['email'], '1234+synthetic-user@users.noreply.github.com')
        self.assertNotIn('SYNTHETIC_SECRET_TOKEN', json.dumps(result))
        for file in Path(result['outputDir']).rglob('*'):
            if file.is_file():
                self.assertNotIn(b'SYNTHETIC_SECRET_TOKEN', file.read_bytes())
    def test_foreign_branch_and_foreign_pages_never_mutated(self):
        for api in [FakeGitHub(foreign=True), FakeGitHub(pages_foreign=True), FakeGitHub(project_id='anotherProject')]:
            with self.assertRaises(DeskError):
                self.run_job('deploy', options=self.options(), client=api)
            self.assertTrue(all(method == 'GET' for method, _, _ in api.calls))
    def test_drift_stops_ref_update_and_orphan_first_publish(self):
        api = FakeGitHub(drift=True)
        with self.assertRaises(DeskError) as caught:
            self.run_job('deploy', options=self.options(), client=api)
        self.assertEqual(caught.exception.code, 'REVISION_CHANGED')
        self.assertFalse(any('/git/refs' in path for _, path, _ in api.calls))
        api = FakeGitHub(existing=False)
        self.run_job('deploy', options=self.options(), client=api)
        commit = next(data for _, path, data in api.calls if path.endswith('/git/commits'))
        self.assertEqual(commit['parents'], [])
        tree = next(data for _, path, data in api.calls if path.endswith('/git/trees'))
        self.assertNotIn('base_tree', tree)
    def test_custom_domain_build_status_and_partial_success(self):
        for api, expected in [(FakeGitHub(built=True), 'built'), (FakeGitHub(fail_pages=True), 'configuration_required')]:
            result = self.run_job('deploy', options={**self.options(), 'domain': 'studio.example.com'}, client=api)
            self.assertEqual(result['pagesStatus'], expected)
            with zipfile.ZipFile(result['zipPath']) as archive:
                self.assertEqual(archive.read('CNAME'), b'studio.example.com\n')
                self.assertIn(b'https://studio.example.com/', archive.read('sitemap.xml'))
                self.assertNotIn(b'https://studio.example.com/site/', archive.read('sitemap.xml'))
        result = self.run_job('deploy', options=self.options(), client=FakeGitHub())
        with zipfile.ZipFile(result['zipPath']) as archive:
            self.assertNotIn('CNAME', archive.namelist())
            self.assertIn(b'https://owner.github.io/site/', archive.read('sitemap.xml'))
    def test_isolated_entry_no_traceback_or_token_echo(self):
        script = Path(worker.__file__)
        request = {'task': 'build', 'project': fixture(), 'options': {}, 'outputDir': self.output()}
        result = subprocess.run([sys.executable, '-I', '-B', str(script)], input=json.dumps(request).encode(), capture_output=True, check=True)
        self.assertEqual(result.stderr, b'')
        self.assertTrue(json.loads(result.stdout)['ok'])
        result = subprocess.run([sys.executable, '-I', '-B', str(script)], input=b'{invalid SYNTHETIC_SECRET_TOKEN', capture_output=True, check=True)
        self.assertNotIn(b'SYNTHETIC_SECRET_TOKEN', result.stdout + result.stderr)
        self.assertNotIn(b'Traceback', result.stdout + result.stderr)
        self.assertFalse(json.loads(result.stdout)['ok'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
