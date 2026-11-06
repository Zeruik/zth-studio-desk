"""Explicit GitHub Pages publishing. Fixed HTTPS origin, no stored credentials."""
import base64
import hashlib
import json
import re
import ssl
import urllib.error
import urllib.request
from urllib.parse import quote
from validation import DeskError, domain, fail

BRANCH = "zth-site"
MARKER = ".zth-desk-owner.json"
API_VERSION = "2026-03-10"


def owner_marker(project_id):
    return {'format': 'zth-desk-site-owner', 'schema': 1, 'projectKey': hashlib.sha256(('zth-desk:' + project_id).encode('utf-8')).hexdigest()}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class GitHub:
    def __init__(self, token):
        if not isinstance(token, str) or not re.fullmatch(r"[A-Za-z0-9_]{10,255}", token):
            fail("TOKEN_INVALID", "请输入本次部署使用的 GitHub token / Enter a GitHub token for this deployment.")
        self.token = token
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect(), urllib.request.HTTPSHandler(context=ssl.create_default_context()))

    def request(self, method, path, data=None, missing=False):
        if (not path.startswith('/repos/') and path != '/user') or not re.fullmatch(r"/[A-Za-z0-9_./?=&%+-]+", path) or '..' in path:
            fail("API_PATH_INVALID")
        body = None if data is None else json.dumps(data, ensure_ascii=True, separators=(',', ':')).encode()
        request = urllib.request.Request('https://api.github.com' + path, data=body, method=method, headers={'Accept': 'application/vnd.github+json', 'Authorization': 'Bearer ' + self.token, 'X-GitHub-Api-Version': API_VERSION, 'User-Agent': 'ZTH-Studio-Desk/1.0.0', 'Content-Type': 'application/json'})
        try:
            with self.opener.open(request, timeout=30) as response:
                data = response.read(32 * 1024 * 1024 + 1)
                if len(data) > 32 * 1024 * 1024:
                    fail('GITHUB_RESPONSE_LIMIT')
                return json.loads(data) if data else {}
        except urllib.error.HTTPError as error:
            status = error.code
            error.close()
            if missing and status == 404:
                return None
            code = {401: 'GITHUB_AUTH', 403: 'GITHUB_PERMISSION', 404: 'GITHUB_NOT_FOUND', 409: 'GITHUB_CONFLICT', 422: 'GITHUB_REJECTED', 429: 'GITHUB_RATE_LIMIT'}.get(status, 'GITHUB_HTTP')
            fail(code, 'GitHub 请求未完成（HTTP ' + str(status) + '）；检查权限、仓库和服务状态 / GitHub request failed (HTTP ' + str(status) + '); check permissions, repository and service status.')
        except (urllib.error.URLError, TimeoutError, OSError):
            fail('NETWORK_FAILED', '无法安全连接 GitHub；请检查网络后重试 / Secure GitHub connection failed; check the network and retry.')
        except (ValueError, UnicodeError):
            fail('GITHUB_RESPONSE_INVALID', 'GitHub 返回了无法识别的响应 / GitHub returned an invalid response.')


def sha(value):
    if not isinstance(value, str) or not re.fullmatch(r'[a-f0-9]{40,64}', value):
        fail('GITHUB_RESPONSE_INVALID')
    return value


def target(options):
    if options.get('confirmPublic') is not True:
        fail('PUBLIC_CONFIRMATION_REQUIRED', '请先确认公开发布目标 / Confirm the public publishing target first.')
    owner, repo = options.get('owner'), options.get('repo')
    if not isinstance(owner, str) or not re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?', owner):
        fail('REPOSITORY_INVALID')
    if not isinstance(repo, str) or not re.fullmatch(r'[A-Za-z0-9_][A-Za-z0-9_.-]{0,99}', repo) or '..' in repo or repo.endswith('.git'):
        fail('REPOSITORY_INVALID')
    return owner, repo


def check_pages(page):
    if page is not None and not isinstance(page, dict):
        fail('GITHUB_RESPONSE_INVALID')
    if page is not None and (page.get('build_type') == 'workflow' or page.get('source', {}).get('branch') != BRANCH or page.get('source', {}).get('path') != '/'):
        fail('FOREIGN_PAGES', '已有 Pages 使用其他发布源，未做任何接管 / Existing Pages uses another publishing source; no takeover was attempted.')


def deploy(project, files, options, client=None):
    owner, repo = target(options)
    custom = domain(options.get('domain', project['site']['domain']))
    api = client or GitHub(options.get('token'))
    prefix = '/repos/' + owner + '/' + repo
    user = api.request('GET', '/user')
    login, user_id = user.get('login'), user.get('id')
    if not isinstance(login, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9-]{0,38}', login) or type(user_id) is not int or user_id < 1:
        fail('GITHUB_RESPONSE_INVALID')
    author = {'name': login, 'email': str(user_id) + '+' + login + '@users.noreply.github.com'}
    repository = api.request('GET', prefix)
    default_branch = repository.get('default_branch')
    if not isinstance(default_branch, str) or not default_branch or default_branch == BRANCH:
        fail('REPOSITORY_INITIALIZE', '请使用已用 README 初始化、且默认分支不是 zth-site 的仓库 / Use a repository initialized with a README whose default branch is not zth-site.')
    default_ref = api.request('GET', prefix + '/git/ref/heads/' + quote(default_branch, safe=''), missing=True)
    if default_ref is None:
        fail('REPOSITORY_INITIALIZE', '请先在 GitHub 用 README 初始化仓库 / Initialize the repository with a README on GitHub first.')
    pages = api.request('GET', prefix + '/pages', missing=True)
    check_pages(pages)
    ref_path = prefix + '/git/ref/heads/' + BRANCH
    ref = api.request('GET', ref_path, missing=True)
    head = sha(ref['object']['sha']) if ref else None
    if head:
        marked = api.request('GET', prefix + '/contents/' + MARKER + '?ref=' + head, missing=True)
        try:
            if not marked or marked.get('encoding') != 'base64' or marked.get('size', 0) > 2048:
                raise ValueError()
            mark = json.loads(base64.b64decode(marked['content'].replace('\n', ''), validate=True))
            if mark != owner_marker(project['id']):
                raise ValueError()
        except (ValueError, KeyError, TypeError):
            fail('FOREIGN_BRANCH', '已有 zth-site 缺少本项目所有权标记，已停止 / Existing zth-site lacks this project ownership marker; stopped.')
    elif pages is not None:
        fail('FOREIGN_PAGES', 'Pages 已存在但本项目分支不存在，已停止 / Pages exists without this project branch; stopped.')
    published = dict(files)
    published[MARKER] = (json.dumps(owner_marker(project['id']), sort_keys=True) + '\n').encode()
    # Every tree starts empty. No private source tree or operations are inherited.
    entries = []
    for name, data in sorted(published.items()):
        blob = api.request('POST', prefix + '/git/blobs', {'content': base64.b64encode(data).decode('ascii'), 'encoding': 'base64'})
        entries.append({'path': name, 'mode': '100644', 'type': 'blob', 'sha': sha(blob.get('sha'))})
    tree = api.request('POST', prefix + '/git/trees', {'tree': entries})
    commit = api.request('POST', prefix + '/git/commits', {'message': 'Publish website with ZTH Studio Desk', 'tree': sha(tree.get('sha')), 'parents': [head] if head else [], 'author': author, 'committer': author})
    new_sha = sha(commit.get('sha'))
    latest = api.request('GET', ref_path, missing=True)
    if (sha(latest['object']['sha']) if latest else None) != head:
        fail('REVISION_CHANGED', '远程分支在部署期间改变，未更新分支；请重新检查 / Remote branch changed during deployment; no branch update was made. Review and retry.')
    check_pages(api.request('GET', prefix + '/pages', missing=True))
    if head:
        api.request('PATCH', prefix + '/git/refs/heads/' + BRANCH, {'sha': new_sha, 'force': False})
    else:
        api.request('POST', prefix + '/git/refs', {'ref': 'refs/heads/' + BRANCH, 'sha': new_sha})
    url = 'https://' + custom + '/' if custom else 'https://' + owner.lower() + '.github.io/' + ('' if repo.lower() == owner.lower() + '.github.io' else repo + '/')
    result = {'uploaded': True, 'branch': BRANCH, 'commit': new_sha, 'repositoryUrl': 'https://github.com/' + owner + '/' + repo, 'url': url, 'publicFiles': len(published), 'pagesStatus': 'pending', 'buildVerified': False, 'live': False, 'warnings': [], 'remoteCommitCannotBeUndoneByCancel': True}
    try:
        source = {'branch': BRANCH, 'path': '/'}
        if pages is None:
            api.request('POST', prefix + '/pages', {'source': source, 'build_type': 'legacy'})
        api.request('PUT', prefix + '/pages', {'source': source, 'build_type': 'legacy', 'cname': custom or None})
        current = api.request('GET', prefix + '/pages')
        if not isinstance(current, dict):
            fail('GITHUB_RESPONSE_INVALID')
        check_pages(current)
        certificate_ready = current.get('https_certificate', {}).get('state') == 'approved'
        if not custom or certificate_ready:
            try:
                api.request('PUT', prefix + '/pages', {'https_enforced': True})
            except DeskError:
                result['warnings'].append('HTTPS 设置尚未完成，请在仓库 Pages 设置确认 / HTTPS enforcement is pending; check repository Pages settings.')
        else:
            result['warnings'].append('自定义域名证书尚未签发，待 DNS/证书就绪后在 Pages 启用 HTTPS / Custom-domain certificate is pending; enable HTTPS in Pages after DNS and certificate readiness.')
        build = api.request('GET', prefix + '/pages/builds/latest', missing=True)
        if build and build.get('commit') == new_sha and build.get('status') == 'built':
            result['pagesStatus'], result['buildVerified'] = 'built', True
        elif build and build.get('commit') == new_sha and build.get('status') == 'errored':
            result['pagesStatus'] = 'failed'
        result['warnings'].append('已区分上传与构建；未探测公网网页，请打开网址验证 / Upload and build are separate; open the URL to verify public availability.')
    except DeskError as error:
        result['pagesStatus'] = 'configuration_required'
        result['warnings'].append('文件提交已成功，但 Pages 配置或状态查询未完成 / Files were committed, but Pages configuration/status is incomplete. ' + error.code)
    return result
