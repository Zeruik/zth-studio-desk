# Studio Desk 1.0.0 API / 引擎协议

这是本地应用与独立 Python 子进程之间的协议，不是可公开监听的 HTTP 服务。标准输出只含一个 UTF-8 JSON 响应；没有服务器端口、pip 依赖或 shell 命令执行。

This is a local process protocol, not an HTTP server. One request produces one UTF-8 JSON response. The worker uses only the Python standard library and invokes no shell.

## Invocation / 调用

```text
python -I -B python/worker.py
```

主进程通过 stdin 发送 UTF-8 JSON，并关闭输入流。最大输入 32 MiB，包括 Base64 图片、运营内容和结构开销。不要通过命令行参数、环境变量或临时请求文件传递 Token。隔离 Python 显式添加的唯一模块目录是受信任 `worker.py` 所在目录。

Send JSON on stdin and close the input stream. The 32 MiB bound includes encoded assets and structural overhead. Never put credentials in command arguments, environment variables or temporary request files. The worker adds only its own trusted code directory to `sys.path`.

```json
{"task":"build","project":{"format":"zth-desk-project","schema":1},"options":{"pageSlug":"index"},"outputDir":"D:/Desk/data/exports/example/job1"}
```

上面只展示请求结构，`project` 必须提供完整项目，不能只传两个字段。`outputDir` 必须已存在、绝对且为空，不得经过 symlink/junction。主进程负责创建每个任务唯一目录、校验它处于自己的数据根目录；引擎再次检查并只在这个目录内写固定产物。不覆盖已有产物，不读取用户提供的源文件路径。

The example abbreviates the project. Supply the complete schema below. The output directory must already exist, be empty and absolute, and contain no symlink/junction traversal. The host must constrain it to its data root; the worker independently confines all writes to it and never imports arbitrary filesystem paths.

Success: `{"ok":true,"result":{...}}`. Failure: `{"ok":false,"error":{"code":"...","message":"中文 / English"}}`. 错误只返回受控消息，不返回上游响应正文、Token、异常对象或 traceback。成功退出也可能包含 `ok:false`；调用方必须检查 JSON，不能只看进程退出码。

Errors expose controlled bilingual messages, not provider response bodies, credentials or tracebacks. Always inspect `ok`; a successfully terminated process can report an application error.

## Tasks / 任务

| Task | Options | Result |
|---|---|---|
| `build` | 可选 `pageSlug`，默认 `index` / optional preview page | `files`, `siteDir`, `zipPath`, `artifactPath`, `outputDir`, `previewHtml`, `report` |
| `audit` | `{}` | `report:{errors:[],warnings:[]}`, `outputDir` |
| `backup` | `{}` | `artifactPath`, `path`, `outputDir`, `private:true`, `encrypted:false` |
| `calendar` | `{}` | 同上路径 / paths; `events`, `private:true` |
| `drafts` | `{}` | 同上路径 / paths; `drafts`, `private:true` |
| `dns` | `{}` | `domain`, `resolved`, `addresses`, `matchesGithubPagesAddress`, `ownershipVerified:false`, `tlsVerified:false`, `message` |
| `deploy` | `owner`, `repo`, `token`, `confirmPublic:true`, 可选 `domain` | 网站产物路径加 / site paths plus `uploaded`, `commit`, `branch`, `repositoryUrl`, `url`, `pagesStatus`, `buildVerified`, `live:false`, `warnings` |

`previewHtml` 内嵌 CSS 与已引用图片，适合 sandbox iframe；站点磁盘文件仍使用相对图片和页面链接。预览导航需要宿主按 `pageSlug` 重新构建，不将 iframe 变成有权访问磁盘的浏览器。`files` 只列网站相对文件名及字节数。manifest 列每个非 manifest 文件的 SHA256，避免自身递归校验。

The preview is self-contained and intended for a sandboxed iframe. Its page navigation is handled by requesting another `pageSlug`, not by granting filesystem access. The site ZIP remains an ordinary static website. The manifest hashes every generated file except itself.

桌面主进程要求先在当前会话构建当前网站内容，记录公开内容摘要；部署时摘要必须一致。编辑网站后请重新构建并检查，再发布。Python worker 自身重新验证/生成内容；会话确认与构建摘要守卫由可信原生主进程负责。

The desktop host requires a successful build of the current public site in the same session before deployment, with a matching site digest. Rebuild and review after editing. Python revalidates and regenerates the site; the trusted native host owns the session-level confirmation and digest guard.

日历将有日期的任务导出为全天事件，结束日是下一天，不自动邀请或通知任何人。无日期任务不进入日历。Markdown 和完整备份均为私有导出。DNS 只查询 `site.domain` 的本机地址解析，不抓取网页、不修改 DNS、不验证所有权或 TLS。

The calendar exports dated tasks as all-day events with an exclusive next-day end, and sends no invitations. Undated tasks are omitted. DNS uses only `site.domain` and reports local resolver observations without changing records or proving ownership/TLS.

## Project schema / 项目结构

完整形状见 [CONTRACT.md](CONTRACT.md)。未知字段、未来 schema、重复编号和非法类型被拒绝。格式为 `format=zth-desk-project`, `schema=1`；`producer` 是合法 semver，本版本保存时写 `1.0.0`，兼容检查以 schema 和严格字段为准，导入不抹除原 producer。必需顶层字段：`id,name,updatedAt,settings,operations,site`；`updatedAt` 为 UTC ISO 时间，如 `2026-11-06T08:00:00.000Z`。

Unknown fields, unsupported schemas, duplicate IDs and invalid types are rejected. Valid producer semver is preserved on import; native saving updates it to the saving app version. Each ID matches `[A-Za-z][A-Za-z0-9_-]{0,63}`. IDs and slugs exclude Windows device names such as CON and NUL. A website has exactly one `index` page; other slugs use lowercase ASCII letters/digits separated by hyphens, at most 64 characters.

| 字段 / Field | 上限 / Limit |
|---|---|
| 项目名 / Project name | 120 characters |
| 标题、按钮标签 / Titles and button labels | 160 characters |
| 网站描述 / Site description | 2,000 characters |
| 区块与子项正文 / Section and item body | 16,000 characters each |
| 任务 / Tasks | 500; owner 80; notes 8,000 characters |
| 草稿 / Drafts | 200; body 64,000; up to 20 unique nonempty tags of 40 characters |
| 页面 / Pages | 20; 30 sections/page; 30 items/section |
| 图片 / Assets | 20; decoded 5 MiB each, 20 MiB total; PNG/JPEG/WebP signatures checked |
| 图片文字 / Image metadata | name 160; alt 500 characters |
| 链接 / Links | 2,048 characters |

只有显式出现在网站区块中的图片会公开。SVG、HTML 和任意文件路径都不是合法图片。链接允许公共 HTTPS、`mailto:`、`tel:` 或 `./slug.html#sectionId`。自定义域名只填 hostname，自动 IDNA 标准化；不接受协议、端口、凭据、IP 或本地域名。`basePath` 可留空或为 `/repo-name/`，只影响 canonical/sitemap，文件与导航始终相对。部署时会按实际 GitHub Pages 目标计算 canonical 基路径，自定义域名使用根路径。

Only explicitly referenced images become public. No SVG or arbitrary files are imported. Links are limited to public HTTPS, email, telephone or a project page/section. Domain input is a hostname; base paths affect canonical/sitemap URLs only. Deployment derives the correct canonical base for repository Pages or a custom domain.

## Failure and cancellation / 失败与取消

常见代码：`SCHEMA_UNSUPPORTED`、`PROJECT_INVALID`、`LINK_INVALID`、`IMAGE_LIMIT`、`OUTPUT_NOT_EMPTY`、`OUTPUT_LINK`、`SITE_AUDIT_FAILED`、`FOREIGN_BRANCH`、`FOREIGN_PAGES`、`REVISION_CHANGED`、`GITHUB_PERMISSION`、`NETWORK_FAILED`。用户可修改输入后创建新任务，不要复用失败任务的输出目录。

Local outputs can be partial after interruption; they are never silently treated as a complete build. The native host terminates cancelled workers. A completed remote commit cannot be cancelled or rolled back by killing a process. If upload succeeded but Pages configuration failed, the result retains `uploaded:true` and `pagesStatus:configuration_required`. Network loss during a remote write can leave its outcome uncertain; inspect the repository before retrying.

## Tests / 测试

`python -I -B qa/worker_test.py` uses synthetic data and a fake GitHub client. It checks output content, byte hashes, privacy separation, malformed inputs, calendar folding, branch ownership, non-force updates, drift, custom-domain paths and partial success. It performs no real deployment or DNS write.
