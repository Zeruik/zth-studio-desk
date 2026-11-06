# Changelog / 更新日志

## 1.0.0 — 2026-11-06

首个独立 ZTH Studio Desk 桌面版本。它不修改已有 Academy、Screen Studio 或 Studio Forge 的项目、数据或安装配置。

First independent ZTH Studio Desk release. Existing Academy, Screen Studio and Studio Forge projects, data and installations remain separate.

- 本地项目格式 `zth-desk-project` schema 1，私有运营任务/日历/草稿与公开网站数据分开。Local project schema 1 separates private operations from public website content.
- 三种网站主题、七种区块、多页相对导航、图片与纯文本安全生成、SEO 描述与 canonical/sitemap。Three site themes, seven section types, relative multipage navigation, safe images/text and SEO metadata.
- 自包含沙盒预览、内部链接与锚点检查、公开 ZIP 和逐文件 SHA256 manifest。Self-contained sandbox preview, internal-link audit, public ZIP and SHA256 file manifest.
- 全项目明文 `.zthdesk` 备份、RFC-style UTF-8 折行 ICS 和 Markdown 草稿导出。Complete unencrypted project backup, folded UTF-8 ICS and Markdown exports.
- 标准库 Python 3.14.10 隔离 worker；输入与输出位置受限，所有 runtime 随发行包提供，无 pip/PATH 修改。Isolated standard-library worker with bundled runtime and bounded input/output.
- GitHub Pages 显式发布、项目所有权摘要、专用 `zth-site`、非 force 更新、远程版本漂移检查、只用 GitHub 用户名和 noreply 提交邮箱。Explicit Pages deployment with ownership marker, dedicated branch, non-force revision checks and username/noreply attribution.
- 区分文件上传、提供商构建与实际站点可达性；域名配置与 DNS 查询只报告已观察到的事实。Upload, provider build and public availability remain distinct.
- 回归测试使用合成数据和模拟部署响应，不执行客户网站发布。Regression tests use synthetic data and mocked deployment responses.

Known limits / 已知范围：本版本不提供多人在线协作、云同步、任意 HTML/JavaScript 插件、微信/Canva 自动发送、系统后台定时任务、DNS 自动修改或外部链接抓取。日历为全天日期，网站联系区块没有后端表单服务。GitHub 仓库须先初始化；取消无法撤回已提交的远程版本。

This release does not provide online collaboration, cloud sync, arbitrary HTML/JS plugins, automatic social posting, OS-level scheduling, DNS mutation or external-link crawling. Calendar events are all-day dates. Contact sections have no form backend. GitHub repositories must be initialized; cancellation cannot undo a completed remote commit.
