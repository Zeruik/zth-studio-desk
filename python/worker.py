"""One bounded JSON request on stdin, one redacted JSON response on stdout."""
import sys
from pathlib import Path
# The isolated embedded interpreter excludes script/cwd paths. Trust only our own code directory.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import datetime as dt
import csv
import io
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


def compact_project(project):
    data = json.dumps(project, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf-8')
    if len(data) > MAX_REQUEST:
        fail('PROJECT_TOO_LARGE')
    return data + (b'\n' if len(data) < MAX_REQUEST else b'')


def handoff(project):
    """A private working handoff, intentionally separate from public site generation."""
    ws = project['workspace']
    lines = ['# ' + project['name'].replace('\n', ' '), '', '> 私有项目交接 / PRIVATE PROJECT HANDOFF', '', '此包包含项目内部资料，不是公开网站。 / This package contains internal project data; do not publish it as a website.', '', '## 项目说明 / Brief', '', ws['brief'], '', '## 验收标准 / Acceptance', '', ws['acceptance'], '', '## 任务与关联 / Tasks and targets', '']
    for task in project['operations']['tasks']:
        target = task['target']
        lines.extend(['### ' + task['title'].replace('\n', ' '), '', '- ID: ' + task['id'], '- Status: ' + task['status'], '- Due: ' + (task['due'] or '—'), '- Owner: ' + task['owner'].replace('\n', ' '), '- Target: ' + target['kind'] + (' / ' + target['ref'] if target['ref'] else ''), '', task['notes'], ''])
    lines.extend(['## 物料 / Bill of materials', '', '详见 BOM.csv；合计是数量 × 单价，不含货币换算或税费。 / See BOM.csv; totals are quantity × unit cost, without tax or currency conversion.', '', 'Total: ' + format(sum(x['quantity'] * x['unitCost'] for x in ws['bom']), '.12g'), '', '## 资料与环境计划 / Resources and environment plans', ''])
    for resource in ws['resources']:
        lines.extend(['### ' + resource['title'].replace('\n', ' '), '', '- Kind: ' + resource['kind'], '- URL: ' + resource['url'], '', resource['notes'], ''])
    lines.extend(['## 显示屏 / Display', '', 'screen.project.zthscreen 是可编辑设计；代码需在工作台内单独生成 ZIP。 / screen.project.zthscreen is editable design data; generate firmware code separately in the workspace.' if ws['screen'] else '本项目未添加显示屏设计。 / No screen design is attached.', '', '完整 project.zthdesk 是未加密 JSON，可用于恢复项目。此包不含本机环境安装缓存、日志、部署 Token 或自动执行脚本。 / The complete project.zthdesk is unencrypted JSON for restoration. No local installation caches, logs, deployment tokens or automatically executable scripts are added.'])
    stream = io.StringIO(newline='')
    writer = csv.writer(stream, lineterminator='\r\n')
    writer.writerow(['ID', 'Name', 'Quantity', 'Unit', 'Unit cost', 'Subtotal', 'Status', 'URL', 'Notes'])
    def cell(value):
        value = str(value)
        candidate = value.lstrip('\ufeff \t\r\n\v\f')
        return "'" + value if candidate[:1] in ('=', '+', '-', '@') else value
    for entry in ws['bom']:
        writer.writerow([cell(entry['id']), cell(entry['name']), entry['quantity'], cell(entry['unit']), entry['unitCost'], entry['quantity'] * entry['unitCost'], entry['status'], cell(entry['link']), cell(entry['notes'])])
    files = {'project.zthdesk': compact_project(project), 'PROJECT.md': ('\n'.join(lines) + '\n').encode('utf-8'), 'BOM.csv': b'\xef\xbb\xbf' + stream.getvalue().encode('utf-8')}
    for index, draft in enumerate(project['operations']['drafts'], 1):
        data = '# ' + draft['title'].replace('\n', ' ') + '\n\nTags: ' + ', '.join(draft['tags']) + '\n\n' + draft['body'] + '\n'
        files['drafts/' + str(index).zfill(3) + '-' + draft['id'] + '.md'] = data.encode('utf-8')
    if ws['screen'] is not None:
        files['screen.project.zthscreen'] = json.dumps(ws['screen'], ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    return files


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
    allowed = {'build': {'pageSlug'}, 'audit': set(), 'backup': set(), 'handoff': set(), 'calendar': set(), 'drafts': set(), 'dns': set(), 'deploy': {'owner', 'repo', 'token', 'domain', 'confirmPublic'}}
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
    if task == 'handoff':
        files = handoff(project)
        artifact = output.zip('private-handoff.zip', files)
        return {'artifactPath': artifact, 'zipPath': artifact, 'outputDir': str(output.root), 'private': True, 'encrypted': False, 'files': [{'path': name, 'size': len(data)} for name, data in sorted(files.items())]}
    if task == 'backup':
        name, data = 'project.zthdesk', compact_project(project)
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
