# Changelog / 更新日志

## 2.0.0 — Integrated workspace

- 统一为赋形造物工作台，署名理工阿白菌（阿白菌 / TechABJ）；赋形造物工作室为向阳科创工作室旗下子工作室。MIT代码许可与原图形权利分开保留。 Correct studio/creator attribution with unchanged MIT code terms.
- schema 2 增加工程简报、验收标准、BOM、资源、屏幕工程和任务目标；兼容 schema 1，保存前保留原件备份。 Schema 2 adds engineering workspace data while retaining schema 1 import/migration.
- 共用一个桌面运行时，集成隔离的 Screen Studio 编辑器与 Forge 环境服务。 Screen and Forge modules share the Desk runtime.
- 屏幕工程由当前完整项目保存；环境安装仍需独立原生确认，加载或导航不会执行任务。 Screen data stays with the project; environment actions need separate native confirmation.
- 公共网站导出继续排除全部工程/运营私有数据；完整 .zthdesk 保持明文备份格式。 Public site exports exclude the private workspace; complete backups remain unencrypted.
- 保持 Desk AppId、exe、安装目录与 data 存储；升级不修改独立旧工具及其资料。 Stable upgrade identity and installation data; standalone legacy tools are untouched.

本版本的详细验收范围以发布记录为准；模块集成不等于真实硬件接线、烧录或环境安装已在每台电脑验证。 Hardware and machine-specific environment installation need separate acceptance.

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

## 2.1.0 — Engineering experiments

Added a bilingual loaded-divider and RC learning bench: adjustable supply/resistors/load/capacitance, numerical outputs, animated charging curve, pause/reset, prediction feedback and four progressive explanations. Save an experiment directly as a private draft with suggested BOM items and a linked physical-verification task. Ideal analytical model only; no SPICE or hardware validation claim. Reports remain excluded from public websites.

## 2.2.0 — Repeatable experiments

- Restore saved experiment parameters and observation notes from bounded inert snapshots. Older plain-text reports remain readable and unchanged.
- Capture A and compare against B on shared physical time/voltage axes; capacitance changes now visibly change charging speed.
- Return from an experiment draft to the corresponding restored experiment. Unrecorded in-session values survive navigation; permanent recovery requires saving a report.
- Pause/reset stop animation scheduling; final charging values update at the endpoint. Labels follow the selected language.
- Saving failures are visible, duplicate concurrent saves are blocked, and report/BOM/task additions preserve project undo history.
- Snapshot validation rejects invalid ranges and malformed input. No user profiles, saves or developer logs are part of the release.

## 3.0.0 — Guided studio projects

- Three bilingual zero-to-one project starters: desk display, electromagnetic actuator control and studio workshop launch. Each creates a separate project with a brief, suggested BOM, linked tasks and evidence worksheets; no task is auto-marked complete.
- New engineering bench for PWM/freewheeling R-L loads and LED E24 current-limit sizing, with editable parameters, current waveforms, slowed switch animation, explicit ideal-model limits and private design reports/review tasks.
- Ctrl+K command search across tools, tasks, drafts and BOM; direct navigation to the selected item.
- Refined project entry points, responsive layouts, focus states, local transitions, modal backdrop and reduced-motion support. Fixed sidebar horizontal overflow and a rare negative first-frame delta that stopped RC animation.
- Electron updated to 45.3.2 from its official SHA-256-pinned archive. Runtime preparation no longer depends on npm carrying the release binary.
- Stable AppId/schema 2 and privacy projection retained. Publish 3.0.0 as a separate GitHub Release; retain all historical tags/assets.
