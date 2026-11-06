# 发布与域名 / Publishing and domains

官方文档核对日期 / Official documentation checked: **2026-11-06**. GitHub API version pinned by this release: `2026-03-10`. This guide describes Studio Desk's implementation and its explicit limits.

## 先准备可审阅的公开内容 / Prepare the public site

1. 填写网站标题、介绍、页面与图片的替代文本。运营任务、草稿和私有工作空间名称不是网站内容；不要为了发布而把整个 `.zthdesk` 当成 `site.zip`。
2. 执行网站检查，修复缺失的页面或锚点。构建并打开 `index.html` 检查首页、各页导航、窄窗口、图片和外部按钮目标。
3. 查看导出的 `site.zip`。它是普通多页静态网站，上传托管服务时使用 ZIP **内部内容**，不要额外套一层 `site/` 目录。

Review the actual website ZIP before publishing. Check page navigation, mobile widths, images, alt text and destination URLs. Publish the contents at the host's web root. A full project backup contains private operational data and is not a website distribution.

## GitHub Pages

创建或选择仓库；创建时勾选 **Add a README**。GitHub 的 Git refs 接口不能为没有分支的空仓库创建引用，所以本应用会要求先初始化。默认分支应保持 `main` 或你已有的源代码分支，不能设为本应用专用的 `zth-site`。[GitHub references API](https://docs.github.com/en/rest/git/refs)

Create an initialized repository, with a README, before publishing. Studio Desk refuses an empty repository and keeps its publishing branch separate from your default source branch.

在 GitHub 创建仅针对这个仓库的 fine-grained personal access token，并按需要给 Contents、Pages 和 Administration 写权限；Pages 配置还要求相应仓库管理权。只在应用当前部署窗口粘贴，发布后可以撤销 Token；不要放进项目文字、截图或代码。[GitHub Pages API permissions](https://docs.github.com/en/rest/pages/pages)

Use a fine-grained token scoped to the selected repository with the required Contents, Pages and Administration write permissions. The account must be permitted to manage Pages. Paste it only for the current invocation and revoke it when no longer needed.

确认目标 `owner/repo`、公开文件数量和域名后，应用执行：

1. 读取当前仓库与 Pages 配置，拒绝其他站点的发布源。
2. 若存在 `zth-site`，要求它的所有权摘要与本项目一致；没有标记、标记损坏或属于其他项目都停止。
3. 仅从公开网站构造新 Git tree。首次发布为不继承源代码历史的独立根提交；后续提交继承专用分支当前版本。
4. 更新前再次核对分支 SHA 与 Pages 来源，使用非 force 更新。并发改变会停止；不会覆盖 `main`。
5. 配置 Pages 从 `zth-site` 的 `/` 目录构建，并检查服务返回的状态。

The dedicated branch is owned by a SHA256-derived project marker. That marker prevents accidental takeover; it is not an authentication secret. The token still determines repository permissions. Keep the original project backup to preserve the publishing identity. Creating a separate project copy deliberately creates a separate owner identity.

GitHub 接受文件提交后可能仍在构建。`pending` 表示尚未确认这次提交构建完成；`built` 表示 API 报告本次提交已完成构建；`configuration_required` 表示文件已提交但 Pages 配置/查询未完成。**应用不自动探测任意站点 URL，所以 `live` 保持 false。** 请打开网址检查最终页面。取消任务不会撤销已经完成的远程提交。

Upload is not a live-site guarantee. The app compares the reported build commit with the newly uploaded commit, but does not fetch arbitrary public website URLs. Open the result in your browser to verify availability. If a network error interrupts a write, inspect the branch before retrying.

## 自定义域名 / Custom domain

只填写域名，例如 `www.example.com`，不填 `https://`、路径或端口。部署会同时生成 `CNAME` 并配置 Pages 的 `cname`，canonical/sitemap 使用域名根目录，不保留仓库名路径。先在 GitHub 验证/设置域名，再向 DNS 服务商添加解析。子域名的 CNAME 目标是 `<owner>.github.io`，不要写仓库路径；根域名按照 GitHub 的当前 A/AAAA 或 ALIAS/ANAME 文档配置。不要建立通配符记录。[GitHub custom domains](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site)

Configure the domain in GitHub before DNS. A subdomain CNAME points to `<owner>.github.io`, without a repository path. For apex records, use GitHub's documented current addresses or supported alias mechanism. Verify domain ownership and avoid wildcard records. DNS and certificate issuance can take time; the app reports certificate pending instead of pretending HTTPS is ready.

如果使用 Cloudflare，请在该域名的 DNS 页面手动添加记录。初次核对可使用 DNS-only，以便观察直接解析；开启代理之后，地址可能变成 Cloudflare 地址。不要因为 DNS 检查未匹配 GitHub 地址，就擅自认定配置错误或所有权无效。本版本不保存 Cloudflare 凭据，也不调用 Cloudflare 写接口。[Cloudflare DNS record management](https://developers.cloudflare.com/dns/manage-dns-records/how-to/create-dns-records/), [Cloudflare proxy status](https://developers.cloudflare.com/dns/proxy-status/)

Cloudflare changes are manual in this release. A proxied hostname may resolve to Cloudflare rather than GitHub addresses. Studio Desk's DNS action reports the local resolver's observed addresses only; it cannot prove global propagation, ownership or TLS readiness. It never edits nameservers, DNS records or operating-system DNS settings.

## 故障处理 / Troubleshooting

| 结果 / Result | 下一步 / Next step |
|---|---|
| `REPOSITORY_INITIALIZE` | 在 GitHub 初始化 README / Initialize a README on GitHub |
| `GITHUB_AUTH` / `GITHUB_PERMISSION` | 检查 Token 对应仓库、权限、账号策略与到期时间 / Check token scope, account policy and expiry |
| `FOREIGN_BRANCH` / `FOREIGN_PAGES` | 核对是否选错仓库或项目；不要删除别人的内容来绕过保护 / Check repository/project identity; do not delete unrelated work to bypass the guard |
| `REVISION_CHANGED` | 查看远程新提交，确认后重新发布 / Review remote changes before publishing again |
| `configuration_required` | 文件可能已提交；打开仓库 Settings → Pages 查看 / Files may already be committed; inspect repository Pages settings |
| DNS 未匹配 / DNS mismatch | 检查 hostname、DNS-only/代理状态和传播；不等于 TLS 失败 / Check hostname, proxying and propagation; this is not a TLS verdict |
| 新版本仍显示旧页面 / Old page | 对照目标 commit、构建状态和浏览器缓存 / Compare target commit, build state and browser cache |

## 其他静态托管 / Other static hosts

可将网站 ZIP 内容手动放入支持静态 HTML 的服务。`./assets/...` 与 `./about.html` 等相对链接支持根目录和仓库子目录，不需要 SPA 重写。域名及 `basePath` 只用于 sitemap/canonical。提供商的登录、费用、配额和使用条款由用户自行确认；本版本只自动化 GitHub Pages，不包含其他平台的一键发布。

Any static HTML host can serve the exported files. Relative links work under a root or subdirectory without SPA rewrites. Configure the canonical hostname/base path for the final location. Automated publishing in this release is limited to GitHub Pages; other providers use manual upload.
