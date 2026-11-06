"""One bounded JSON request on stdin, one redacted JSON response on stdout."""
import sys
from pathlib import Path
# The isolated embedded interpreter excludes script/cwd paths. Trust only our own code directory.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import datetime as dt
import json
import os
import re
import socket
import zipfile
from validation import DeskError, domain, fail, obj, validate
from sitegen import audit, generate
from github_pages import deploy, target

MAX_REQUEST = 32 * 1024 * 1024


def pairs_unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            fail('JSON_DUPLICATE', 'JSON 字段重复 / Duplicate JSON field.')
        result[key] = value
    return result


def parse(data):
    try:
        return json.loads(data.decode('utf-8-sig'), object_pairs_hook=pairs_unique, parse_constant=lambda _: fail('JSON_INVALID'))
    except (UnicodeError, ValueError, RecursionError):
        fail('JSON_INVALID', '输入不是有效的 UTF-8 JSON / Input is not valid UTF-8 JSON.')


class Output:
    def __init__(self, raw):
        if not isinstance(raw, str) or not raw or '\x00' in raw:
            fail('OUTPUT_INVALID')
        supplied = Path(raw)
        if not supplied.is_absolute() or '..' in supplied.parts:
            fail('OUTPUT_INVALID', '输出目录必须是明确的绝对路径 / Output directory must be an explicit absolute path.')
        self.root = supplied.resolve(strict=True)
        if not self.root.is_dir():
            fail('OUTPUT_INVALID')
        for part in [supplied] + list(supplied.parents):
            if part.is_symlink() or getattr(os.path, 'isjunction', lambda _: False)(part):
                fail('OUTPUT_LINK', '输出目录不能经过符号链接或联接点 / Output directory may not traverse symlinks or junctions.')
        if any(self.root.iterdir()):
            fail('OUTPUT_NOT_EMPTY', '请为本次任务使用新的空目录 / Use a new empty output directory for this job.')

    def destination(self, relative):
        if not isinstance(relative, str) or not re.fullmatch(r'[A-Za-z0-9_./-]+', relative) or any(p in ('', '.', '..') for p in relative.split('/')):
            fail('OUTPUT_PATH_INVALID')
        target = self.root.joinpath(*relative.split('/'))
        if not target.is_relative_to(self.root):
            fail('OUTPUT_PATH_INVALID')
        for part in [target] + list(target.parents):
            if part == self.root.parent:
                break
            if part.is_symlink() or getattr(os.path, 'isjunction', lambda _: False)(part):
                fail('OUTPUT_LINK')
        target.parent.mkdir(parents=True, exist_ok=True)
        return target

    def write(self, relative, data):
        target = self.destination(relative)
        with target.open('xb') as stream:
            stream.write(data)
        return str(target)

    def zip(self, relative, files):
        target = self.destination(relative)
        with target.open('xb') as stream, zipfile.ZipFile(stream, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            for name, data in sorted(files.items()):
                if not re.fullmatch(r'[A-Za-z0-9_./-]+', name) or any(p in ('', '.', '..') for p in name.split('/')):
                    fail('OUTPUT_PATH_INVALID')
                entry = zipfile.ZipInfo(name, (2020, 1, 1, 0, 0, 0))
                entry.compress_type = zipfile.ZIP_DEFLATED
                entry.external_attr = 0o100644 << 16
                archive.writestr(entry, data)
        return str(target)


def write_site(output, files, preview, report):
    for name, data in files.items():
        output.write('site/' + name, data)
    zipped = output.zip('site.zip', files)
    return {'files': [{'path': name, 'size': len(data)} for name, data in sorted(files.items())], 'siteDir': str(output.root / 'site'), 'zipPath': zipped, 'artifactPath': zipped, 'outputDir': str(output.root), 'previewHtml': preview, 'report': report}


def ics_escape(value):
    return value.replace('\\', '\\\\').replace('\r', '').replace('\n', '\\n').replace(';', '\\;').replace(',', '\\,')


def fold_line(line):
    result, current = [], ''
    for char in line:
        if len((current + char).encode('utf-8')) > 75:
            result.append(current)
            current = ' '
        current += char
    result.append(current)
    return '\r\n'.join(result)


def calendar(project):
    lines = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//ZTH Studio Desk//Local Calendar 1.0//EN', 'CALSCALE:GREGORIAN', 'METHOD:PUBLISH']
    count = 0
    for task in project['operations']['tasks']:
        if not task['due']:
            continue
        date = dt.date.fromisoformat(task['due'])
        try:
            end = date + dt.timedelta(days=1)
        except OverflowError:
            fail('DATE_INVALID')
        count += 1
        description = 'Owner: ' + task['owner'] + '\nStatus: ' + task['status'] + '\nChannel: ' + task['channel'] + '\n' + task['notes']
        lines.extend(['BEGIN:VEVENT', 'UID:' + project['id'] + '-' + task['id'] + '@zth-studio-desk.local', 'DTSTAMP:' + dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ'), 'DTSTART;VALUE=DATE:' + date.strftime('%Y%m%d'), 'DTEND;VALUE=DATE:' + end.strftime('%Y%m%d'), 'SUMMARY:' + ics_escape(task['title']), 'DESCRIPTION:' + ics_escape(description), 'TRANSP:TRANSPARENT', 'END:VEVENT'])
    lines.append('END:VCALENDAR')
    return ('\r\n'.join(fold_line(line) for line in lines) + '\r\n').encode('utf-8'), count


def markdown(project):
    out = ['# ' + project['name'].replace('\n', ' '), '', '> 私有草稿导出 / Private draft export', '']
    for draft in project['operations']['drafts']:
        out.extend(['## ' + draft['title'].replace('\n', ' '), '', 'ID: `' + draft['id'] + '`', '', 'Tags: ' + ', '.join(t.replace('\n', ' ') for t in draft['tags']), '', draft['body'], '', '---', ''])
    return '\n'.join(out).encode('utf-8')


def dns_check(site, resolver=None):
    host = domain(site['domain'])
    if not host:
        fail('DOMAIN_REQUIRED', '请先填写网站域名 / Enter a website domain first.')
    try:
        records = (resolver or socket.getaddrinfo)(host, 443, type=socket.SOCK_STREAM)
        addresses = sorted({row[4][0] for row in records})
    except (socket.gaierror, OSError):
        return {'domain': host, 'resolved': False, 'addresses': [], 'matchesGithubPagesAddress': False, 'ownershipVerified': False, 'tlsVerified': False, 'message': '当前系统 DNS 未解析成功；可能尚未传播 / System DNS did not resolve this hostname; propagation may be pending.'}
    expected = {'185.199.108.153', '185.199.109.153', '185.199.110.153', '185.199.111.153', '2606:50c0:8000::153', '2606:50c0:8001::153', '2606:50c0:8002::153', '2606:50c0:8003::153'}
    return {'domain': host, 'resolved': bool(addresses), 'addresses': addresses, 'matchesGithubPagesAddress': bool(set(addresses) & expected), 'ownershipVerified': False, 'tlsVerified': False, 'message': '仅为本机解析观察；代理/CDN可能返回不同地址，不证明域名所有权、完整传播或 TLS / This is a local resolver observation. Proxies/CDNs may return other addresses; ownership, global propagation and TLS are not verified.'}


def handle(request, github_client=None):
    request = obj(request, ('task', 'project', 'options', 'outputDir'))
    task = request.get('task')
    allowed = {'build': {'pageSlug'}, 'audit': set(), 'backup': set(), 'calendar': set(), 'drafts': set(), 'dns': set(), 'deploy': {'owner', 'repo', 'token', 'domain', 'confirmPublic'}}
    if not isinstance(task, str) or task not in allowed:
        fail('TASK_INVALID')
    options = obj(request.get('options', {}), allowed[task])
    project = validate(request.get('project'))
    output = Output(request.get('outputDir'))
    if task == 'audit':
        report, _ = audit(project['site'])
        return {'report': report, 'outputDir': str(output.root)}
    if task in ('build', 'deploy'):
        custom = None
        if task == 'deploy':
            owner, repo = target(options)
            custom = domain(options.get('domain', project['site']['domain']))
            project['site']['domain'] = custom or owner.lower() + '.github.io'
            project['site']['basePath'] = '' if custom or repo.lower() == owner.lower() + '.github.io' else '/' + repo + '/'
        files, preview, report = generate(project['site'], options.get('pageSlug', 'index'), custom)
        if task == 'deploy' and report['errors']:
            fail('SITE_AUDIT_FAILED', '内部链接检查失败，修复后再发布 / Fix internal link errors before publishing.')
        result = write_site(output, files, preview, report)
        if task == 'deploy':
            result.update(deploy(project, files, {**options, 'domain': custom}, client=github_client))
            result.pop('previewHtml', None)
        return result
    if task == 'backup':
        name, data = 'project.zthdesk', (json.dumps(project, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
        extra = {'private': True, 'encrypted': False}
    elif task == 'calendar':
        data, count = calendar(project)
        name, extra = 'calendar.ics', {'events': count, 'private': True}
    elif task == 'drafts':
        name, data, extra = 'drafts.md', markdown(project), {'drafts': len(project['operations']['drafts']), 'private': True}
    else:
        return {**dns_check(project['site']), 'outputDir': str(output.root)}
    saved = output.write(name, data)
    return {'artifactPath': saved, 'path': saved, 'outputDir': str(output.root), **extra}


def main():
    try:
        raw = sys.stdin.buffer.read(MAX_REQUEST + 1)
        if len(raw) > MAX_REQUEST:
            fail('REQUEST_TOO_LARGE', '请求超过 32 MiB / Request exceeds 32 MiB.')
        result = handle(parse(raw))
        response = {'ok': True, 'result': result}
    except DeskError as error:
        response = {'ok': False, 'error': {'code': error.code, 'message': error.message}}
    except (OSError, ValueError, TypeError, KeyError, OverflowError, RecursionError):
        response = {'ok': False, 'error': {'code': 'OPERATION_FAILED', 'message': '操作未完成；检查输入、输出目录权限和可用空间，原项目未更改 / Operation failed; check input, output permissions and available space. The original project was not changed.'}}
    except Exception:
        response = {'ok': False, 'error': {'code': 'INTERNAL_ERROR', 'message': '操作未完成；保留原项目后重试 / Operation failed; preserve the original project and retry.'}}
    encoded = (json.dumps(response, ensure_ascii=False, separators=(',', ':')) + '\n').encode('utf-8')
    sys.stdout.buffer.write(encoded)
    sys.stdout.buffer.flush()


if __name__ == '__main__':
    main()
