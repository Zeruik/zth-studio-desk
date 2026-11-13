# 赋形造物工作台 / ZTH Studio Desk 3.0.0

面向小型工作室的本地桌面工作台：在同一个项目里管理工程简报、验收清单、物料、屏幕界面、环境准备、运营任务、活动日历、文案草稿和多页网站。赋形造物工作室是向阳科创工作室旗下的子工作室。创作者与权利人为理工阿白菌（阿白菌 / TechABJ）；代码采用 MIT 许可，原工作室图形标识的权利单独保留。

An integrated local workspace for small studios: project briefs, acceptance criteria, bills of materials, embedded screen design, environment preparation, operations, drafts, events and static websites. 赋形造物工作室 is a subsidiary studio of 向阳科创工作室. Creator and rightsholder: 理工阿白菌（阿白菌 / TechABJ）. Code remains MIT licensed; original artwork retains separate rights.

## 创作者 / Creator

理工阿白菌（阿白菌 / TechABJ）为工作室创作这款软件，专注于将工程学习、动手制作与工作室运营结合起来的工具。公开代码账户为 Zeruik。详细署名和素材权利见 [ATTRIBUTION.md](ATTRIBUTION.md)。

TechABJ created this software for the studio, focusing on tools that bring engineering learning, hands-on making and studio operations together. The public code account is Zeruik. See [ATTRIBUTION.md](ATTRIBUTION.md) for attribution and artwork rights.

## 开始使用 / Start here

1. 解压 Windows 发行包并运行其中的安装程序；安装到可写的英文路径。桌面程序自带 Electron 与 Python，普通用户不需要安装 Python、Node.js、pip 或配置 PATH。
2. 新建空项目，或打开原创虚构示例。填写工作空间名称；这个名称属于私有项目。网站标题、描述、页面文字和引用的图片属于公开内容，发布前分别核对。
3. 在运营视图添加任务、负责人、日期、状态和渠道；在草稿视图编辑文案。它们保存在本地项目中，不会自动发给微信、Canva、GitHub 或任何人。
4. 在网站编辑器添加页面和内容区块、选择主题、调整文字与图片，查看桌面/移动预览。首页的路径固定为 `index.html`，其他页面使用简短英文 slug。
5. 先检查，再构建。导出 `site.zip` 可交给任意静态托管服务；导出完整 `.zthdesk` 用于自己备份或迁移，**两者公开范围不同**。

Extract the Windows release, run its installer, and choose a writable English-only installation path. The app includes Electron and Python; end users need no developer toolchain or PATH changes. Start from an empty project or the original fictional demo. Edit private operations separately from public website content, inspect the preview, run the audit, and export the website ZIP. Keep full project backups private.

## 能做什么 / Capabilities

| Area | 中文 | English |
|---|---|---|
| 项目 / Projects | 本地保存、导入导出完整项目、编辑撤销/重做 | Local projects, complete import/export, editing undo/redo |
| 工程 / Engineering | 简报、验收标准、物料清单和引用资源 | Briefs, acceptance criteria, BOM and resource references |
| 屏幕 / Screen | 集成屏幕编辑与真实代码导出，工程由当前项目保存 | Integrated screen editor and code export, stored in the current project |
| 环境 / Environment | 集成 Forge 检测、方案、执行确认与进度 | Integrated Forge inspection, plans, confirmations and progress |
| 运营 / Operations | 任务状态、日期、负责人、渠道、备注和月历 | Tasks, owners, channels, notes and calendar |
| 草稿 / Drafts | 标题、正文、标签，导出 Markdown | Draft titles, bodies, tags and Markdown export |
| 网站 / Website | Studio、Editorial、Portfolio 三种主题，多页导航，七类内容区块 | Three visual themes, multipage navigation and seven section types |
| 内容 / Sections | 首屏、文字、卡片、图库、FAQ、行动按钮、联系信息 | Hero, text, cards, gallery, FAQ, calls to action and contacts |
| 检查 / Audit | 内部页面与锚点、图片引用和替代文本、网站描述 | Internal pages/fragments, image references/alt text and description |
| 发布 / Publish | 显式确认后发布到 GitHub Pages 专用分支 | Explicitly confirmed publication to a dedicated GitHub Pages branch |
| 导出 / Export | 网站 ZIP、私有完整备份、ICS 日历、Markdown 草稿 | Website ZIP, full private backup, ICS calendar and Markdown drafts |

生成网站使用语义化 HTML、响应式 CSS、本地图片和相对页面链接，没有外部字体、分析脚本或前端框架。图片只从项目内显式引用的 PNG/JPEG/WebP 字节生成；未使用图片和原始本机文件名不进入网站。图片原始字节会保留，因此请在导入前移除不想公开的照片 EXIF/位置元数据。正文按纯文本转义，不执行 HTML 或 JavaScript。FAQ 用原生可展开元素，按钮是实际链接；联系区块不带虚假的表单提交服务。

The exported site uses semantic HTML, responsive CSS, local images and relative navigation. It has no external fonts, analytics, frontend runtime or required hosted database. Image bytes are preserved; remove unwanted EXIF/location metadata before importing photographs. Text is escaped; arbitrary HTML/JavaScript is not executed. FAQ items expand with native browser controls. Contact sections provide real links, not a pretend form backend.

## 保存、迁移与隐私 / Storage and privacy

- 项目文件包含工作空间名称、工程简报、验收标准、物料、屏幕工程、资源引用、运营任务、草稿、设置和图片。完整 `.zthdesk` 备份是可移植 JSON，**没有加密**；不要当作公开网站上传。
- `site.zip` 只有公开的 `site` 内容和生成资源。部署使用相同公开文件，另加一个不含明文项目编号的所有权摘要标记。工程工作区、BOM、屏幕工程、运营内容、Token、历史任务日志、私有项目名称不写入网站或 Git 提交。
- Github Token 只用于当次明确发起的部署，通过子进程标准输入传递，未写入项目、任务历史、命令参数或导出文件。进程结束后不留应用内凭据缓存；这不等于能阻止操作系统级内存检查。
- 更新或卸载前先导出完整项目并检查文件能重新导入。恢复备份时保留原项目身份，才能继续管理对应发布分支；复制为新的项目身份后，不应接管旧身份的网站。
- 手动导出的 ZIP/备份由用户管理；卸载应用不会撤销已公开的网页、远程提交或外部 DNS 设置。删除一个本地项目也不会取消远程发布。

Full project backups are portable **unencrypted JSON**, including private operations and drafts. Website exports contain only public site data. Deployment credentials stay in the current invocation and are not persisted by the app. Back up before updating or uninstalling. Restoring the original project identity preserves ownership of its publishing branch; a duplicated identity is deliberately treated as another project. Uninstallation cannot retract a public site, remote commit, exported backup or DNS record.

## 离线与联网范围 / Offline and online scope

日常编辑、保存、预览、静态构建、链接审计、网站 ZIP、完整备份、日历和草稿导出全部在本地执行。检查不抓取外部 HTTPS 链接，因此不会宣称所有外部链接仍然可访问。GitHub 部署需要联网与用户授权；DNS 检查需要本机 DNS 能解析相应域名。自动构建是应用打开期间的可选功能，不会创建系统启动项或后台计划任务。

Project editing, screen code generation, local website previews/builds/audits and exports run offline. The audit validates internal destinations without crawling external URLs. GitHub deployment and explicit DNS lookups require connectivity. Optional automatic building operates only while the app is open; it does not install an operating-system scheduler or startup service.

### 环境任务的独立边界 / Environment task boundaries

Forge 模块只有在你主动点击时才检测环境。系统安装必须先审阅方案并通过原生确认；导入项目、任务跳转或打开应用不会执行安装。WSL、Ubuntu、ROS、VC++ 与 Build Tools 大型组件没有装入这个 ZIP；相关安装仍可能需要网络、管理员权限和手动重启。取消不等于回滚，卸载工作台不会删除已建立的外部开发环境。屏幕编辑与代码导出也不等于完成真实接线或烧录。

Forge inspects the machine only on explicit action. Environment changes require a reviewed plan and native confirmation; loading a project or following a task target never starts installation. Large WSL/Ubuntu/ROS/Microsoft packages are not bundled and may need network access, administrator rights and a manual restart. Cancellation is not rollback; uninstalling Desk does not remove those environments. Screen code export does not validate physical wiring or flash hardware.

## 升级与整合 / Upgrading and integration

3.0.0 沿用 Desk 1 的安装标识、安装文件夹和 data 存储。schema 1 项目可在内存中迁移到 schema 2，保留原字段；保存迁移结果前会备份原文件字节。升级前仍应另行导出完整项目。换安装目录时，先正常退出并完整复制整个旧目录（包括 data），不要只复制 exe。

Version 2 retains the Desk 1 installer identity, folder and data storage. Schema 1 is migrated in memory without losing existing fields; saving retains a backup of original file bytes. Export an independent backup before upgrading. When changing folders, close the app and copy the complete old folder including data before running Setup.

屏幕与环境模块共享当前桌面运行时；屏幕工程属于当前 .zthdesk 项目，隔离子界面不能直接访问本机接口。旧版独立 Forge、Screen Studio 和 Academy 安装及个人资料不会被自动导入或删除。

Screen and environment modules share the desktop runtime. Screen documents belong to the current .zthdesk project, while the sandboxed child editor has no direct native API. Existing standalone Forge, Screen Studio and Academy installations/data are neither silently imported nor removed.

## 部署与域名 / Publishing and domains

参见 [DEPLOY.md](DEPLOY.md)。请先在 GitHub 创建仓库并勾选初始化 README。应用只使用 `zth-site` 分支；已有分支必须带本项目所有权标记，已有 Pages 必须使用相同发布源。它不会改 `main`，不会强制推送，也不会接管其他站点。

上传成功、GitHub 构建完成、公网页面可以访问是三个不同结果。应用显示 `pending`、`built` 或需要配置等实际状态；不会仅凭 API 接受请求就宣称站点已经上线。自定义域名需要你在域名服务商处配置 DNS，应用不会自动接管 Cloudflare 账户。

See [DEPLOY.md](DEPLOY.md). Use an initialized repository. The app updates only its marked `zth-site` branch with non-force commits and leaves `main` untouched. Upload, provider build and public availability are reported separately. Domain configuration remains an explicit task at your DNS provider.

## 开发与复现 / Development and reproducibility

发布运行时版本及 SHA256 见 `runtime-lock.json`：Windows x64 Electron 45.0.0、Python 3.14.10。Python 引擎只有标准库，四个模块位于 `python/`。使用受信任解释器测试：

```powershell
python -I -B qa/worker_test.py
node qa-backend.cjs ./out/build/studio-desk/payload/runtime/python/python.exe
```

第二条命令使用默认打包目录中的 Python，需先完成开发构建；也可替换为另一个受信任 Python 的路径。引擎协议、字段上限、错误和输出位置见 [API.md](API.md)。开发者打包脚本是 `prepare-runtime.cjs`、`build-release.cjs` 与 `build-product.cjs`；依赖锁文件位于 `build-runtime/`。重新下载运行时及首次开发依赖安装需要网络；收到完整发行 ZIP 的终端用户运行时不需要下载这些组件。

Runtime versions/hashes are pinned in `runtime-lock.json`. The Python worker is standard-library-only and runs with `-I -B`; it adds only its own trusted source directory to the isolated interpreter path. Development dependency acquisition is separate from an end user's offline installation. See [API.md](API.md) for the automation contract and [CHANGELOG.md](CHANGELOG.md) for release scope.

回归测试覆盖合成项目、公开/私有边界、三主题生成、ZIP/manifest、路径与字段拒绝、ICS 折行、模拟 GitHub 所有权/并发保护/部分成功和隔离入口。测试不会发布客户网站，也不证明所有 DNS、GitHub 账号策略或真实网络环境都相同。

Regression tests use synthetic projects and mocked provider responses. They verify real generated files and boundary handling, but do not publish a customer's site or certify every account policy, DNS provider or network environment.

## 3.0 项目与实验 / Guided projects and experiments

从“从零到成品”创建桌面环境屏、电磁执行器或工作室活动项目。创建的是独立新工程，会准备建议物料、任务和证据记录页；需要自己填写单价、接线/编译条件与实际验收结果。快捷搜索 Ctrl+K 可以打开工具、任务、草稿和物料。

The project journeys create independent starter projects with suggested materials, linked tasks and evidence worksheets. They do not claim hardware success. The software path through screen editing, report creation, static-site generation and private handoff was exercised with a synthetic starter project. Physical wiring, flashing, temperature and clone-board pinouts require their own checks.

工程计算台含稳态理想R-L负载的PWM/续流模型与LED限流选阻。前者忽略二极管压降、反电动势和损耗；后者按估计压降选择向上取整的E24标称电阻。结果用于理解和初步设计，不能替代器件数据手册或实测。模型记录留在私有工程，不进入公开网站。

Version 3.0.0 is a new GitHub tag/Release. Existing 1.x/2.x release files remain available. Close the old app, export a backup and upgrade in the same writable installation folder; schema 2 and the AppId are retained.
