# ZTH Studio Desk 5.0.0

把学习、仿真、工程、设计、验收和工作室运营连成一个工作空间。

One workspace for learning, simulation, projects, design, acceptance and studio operations.

- 完整 186 节课程，电子、机械、编程、运营四赛道；12 节新增衔接课，配单位计算、屏幕迁移、框坐标和评价计数操作台。
- 186 lessons across electronics, mechanics, programming and operations; 12 bridge lessons with unit-aware display, box-coordinate and evaluation benches.

- 原创三维教学场景（WebGL 优先，不支持时使用同一三维结构、坐标的矢量绘制并简化光照）：机械臂关节/逆运动学/抓取，四足步态与点击目标，无人机航点、故障与任务；暂停、单步、复位及观察视角。
- Original 3D teaching scenes (WebGL preferred, with a shared-structure vector renderer and simplified lighting and tessellation when unavailable): articulated arm/IK/grasp, quadruped gait and goals, drone waypoints/faults/missions; pause, step, reset and camera controls.

- 内嵌屏幕工程与环境/数据审查；私有简报、BOM、任务、日历、草稿、实验报告与验收记录，区分仿真、编译和实物依据，保留失败与复测历史。
- Integrated screen engineering, environments and data review; private brief, BOM, tasks, calendar, drafts, reports and acceptance evidence. Distinguish simulation/compile/physical results and retain failed/retest history.

- 自带 Python，实际生成静态多页网站、日历和交接 ZIP。私有工程字段不进入公开网站；公开页面中主动填写的内容仍需你自行审阅。
- Bundled Python generates real multipage static sites, calendars and handoff ZIPs. Private project fields are excluded from public sites; content deliberately entered into public pages still needs review.

[GitHub 源码 / Source](https://github.com/Zeruik/zth-studio-desk) · [版本下载 / Releases](https://github.com/Zeruik/zth-studio-desk/releases)

## 平台与安装 / Platforms and installation

| 系统 / OS | 交付形式 / Delivery | 数据 / Data |
|---|---|---|
| Windows 10/11 x64 | 完整 ZIP 内的 Inno Setup；默认勾选桌面快捷方式 / Setup in the complete ZIP; desktop shortcut selected by default | Desk 沿用安装目录 data/；Forge/Screen 使用当前用户配置 / Desk keeps install-relative data; Forge/Screen use per-user storage |
| Linux x64 / ARM64 | DEB、tar.gz；优先使用桌面发行版包管理器 / DEB or tar.gz; prefer the distribution package installer | 当前用户数据目录 / Per-user data |
| macOS Intel / Apple Silicon | .app ZIP、DMG；拖入 Applications / .app ZIP or DMG; move to Applications | 当前用户数据目录，独立于应用 / Per-user data outside the app |

应用运行时随包提供；不需要另装 Node、Python 或浏览器，不修改系统 PATH。Linux 仍依赖正常桌面系统的 GTK/NSS/音频/图形库及 Chromium 沙箱支持；DEB 会声明这些系统依赖并配置自己的沙箱辅助程序。原生平台验收范围以发布说明为准，不代表每一种发行版或显卡都已覆盖。

Application runtimes are bundled: no separate Node, Python or browser install, and no global PATH edits. Linux requires normal desktop GTK/NSS/audio/graphics libraries and Chromium sandbox support. The DEB declares those system dependencies and configures its own sandbox helper. Release notes state native acceptance coverage; this does not cover every distribution or GPU.

macOS 包只有 ad-hoc 完整性签名，没有 Developer ID / Apple notarization，可能需要系统正常的显式打开确认；不要关闭系统安全保护。Windows Setup 同样未做商业代码签名。

macOS builds have an ad-hoc integrity signature, without Developer ID or Apple notarization; normal explicit OS opening approval may be required. Do not disable OS security. Windows Setup is also unsigned.

## 资料、隐私与升级 / Data, privacy and upgrades

默认本地工作，不自动上传资料、数据集、学习档案或运行诊断。只有你主动使用链接、天气或网站发布功能时，相关动作才可能联网。完整工程、验收报告与 CSV 可能包含个人信息，分享前请检查。

Work is local by default. No automatic upload of projects, datasets, learner archives or diagnostics. Explicit links, optional weather and website publishing may use a network. Full projects, acceptance reports and CSV exports may contain personal information; review before sharing.

升级前导出个人资料和项目备份，退出程序，再使用同一应用的新版本。Windows Desk 沿用安装目录和 data；Linux/macOS 替换应用本体，保留用户数据。卸载默认保留个人资料，不替你卸载独立安装的 WSL、ROS 或编译器。不要用旧版本覆盖新存档；不支持的未来格式应保留原件并拒绝写入。

Export learner/project backups and close the app before upgrading. Windows Desk keeps its installation and data folder; Linux/macOS replace the application while retaining user data. Uninstall retains personal data and does not remove separately installed WSL/ROS/compilers. Keep originals when a future format is rejected; do not overwrite newer data with an older app.

Windows 学习档案沿用系统本机保护；Linux/macOS 使用随机本地密钥和 AES-256-GCM，密钥/目录受当前用户权限约束，这不等于系统钥匙串或抵御同账户恶意软件。跨电脑迁移使用有密码的 .zth 导出；完整恢复本机目录需要连同其密钥一起保留。不要把真实存档放进源码仓库。

Windows learner archives retain OS-local protection. Linux/macOS use a random local key with AES-256-GCM and owner-only permissions: this is not an OS keychain or protection against malware running as the same user. Use password-protected .zth exports for migration; complete local directory recovery also requires its key. Never commit real archives to source control.

## 构建 / Build

开发者需要 Node 22、固定的 build-runtime 依赖及相应系统打包工具。先运行 npm ci --prefix build-runtime，再在 Linux/macOS 运行 node cross-platform.cjs --package。构建器从官方来源获取并核对锁定的运行时 SHA-256。GitHub workflow 在标准原生 runner 上启动真实应用、重开资料、验证输出后才打包；只有显式工作流参数才上传到匹配版本的新草稿 Release，禁止覆盖已有资产。

Developers need Node 22, the locked build-runtime dependencies and native packaging tools. Run npm ci --prefix build-runtime, then node cross-platform.cjs --package on Linux/macOS. Official runtime archives are SHA-256 pinned. The workflow runs and reopens the native app and verifies output before packaging; explicit inputs alone permit upload to the matching new draft release. Existing assets are never clobbered.

Windows 使用 Inno Setup 7 和 node build-release.cjs。开发构建首次下载依赖需要网络，成品应用启动无需下载运行时。生成项目的第三方工具、ROS 软件包与实物烧录依赖不等同于应用运行时，按项目 README 单独核对。

Windows builds use Inno Setup 7 and node build-release.cjs. Initial developer dependency downloads require a network; end users do not download application runtimes at launch. Generated-project toolchains, ROS packages and physical flashing dependencies are separate from app runtimes: follow their project README.

## 作者与许可 / Creator and terms

理工阿白菌 / TechABJ 为赋形造物工作室制作，专注于连接工程学习、动手制作与工作室运营。赋形造物工作室是向阳科创工作室旗下子工作室。

Created by TechABJ for Fuxing Zaowu Studio, a sub-studio of Xiangyang Science & Technology Studio, connecting engineering learning, making and studio operations.

原始工具代码按对应 LICENSE 使用；Logo 保留品牌权利。单独标注的 Academy 与机器人原创教学内容适用其内容许可，不因工具代码 MIT 而自动变为 MIT。第三方运行时、字体和库保留各自许可证。

Original tool code follows its LICENSE; logo rights remain reserved. Separately labelled Academy and authored robotics teaching content retain their content terms and are not automatically MIT. Third-party runtimes, fonts and libraries retain their own licenses.

联系 / Contact: zeruik@qq.com · [作者主页 / Creator](https://github.com/Zeruik)
