# ZTH-平面设计器 / ZTH Design Studio

赋形造物工作室（ZeroToHand Studio）出品，作者：理工阿白菌 / TechABJ（GitHub: Zeruik）。面向工作室、社团和项目团队的离线图形设计工具。Windows 桌面端与 Android 预览端共享同一个编辑器和 `.zthpmsj` 工程格式。

An offline graphic design tool by ZeroToHand Studio, created by TechABJ. Windows and the Android preview share the same editor and portable `.zthpmsj` project format. This is an independently packaged preview product, not a full replacement for Canva or Photoshop.

## 开始使用 / Start

Windows：运行 Setup，选择语言，阅读协议并选择安装路径。安装包内置运行时，用户不需要安装 Node.js、Python 或开发环境。支持 Windows 10/11 x64；应用启动时检查系统版本与用户目录写入能力。卸载入口位于开始菜单和系统“已安装的应用”，保留用户的作品和自动保存。

Android：安装 `Android-preview.apk`。需要 Android 9 或更新版本及较新的 Android System WebView。程序不申请网络权限，编辑器、字体、素材和二维码算法都在 APK 内。此 APK 为开发签名预览，尚未经过实体手机的完整验收。

Windows: run Setup, choose a language, review the terms and select an installation path. The runtime is included; no developer tools are needed. Android: install the preview APK on Android 9+ with an up-to-date System WebView. The app contains its assets and has no Internet permission. Physical-device validation remains outstanding.

## 编辑与复用 / Edit and reuse

- 文字、矩形、圆形、三角形、星形、箭头、六边形、平行四边形及自定义多边形；移动、缩放、旋转、描边、透明度、分组和图层顺序。
- 自定义画布、常用比例、图片裁切预览和比例、保持宽高比、翻转、取色抠图、容差、连通区域与边缘柔化。
- 17 套内置模板（含配色变体），覆盖活动、招新、信息卡、研究展板、讲座、作品与产品图。所有模板中的文字与形状都可编辑；照片为嵌入图像。
- 保存当前工程到“我的模板”，或导出同样后缀的模板文件；锁定 LOGO，设置产品图片槽，下次换图保留框架、旋转与层级。
- 规则排版助手：按标题、正文、照片、LOGO、二维码角色生成三种布局。没有大模型，不会理解任意语义或自动达到专业设计师水平。
- 网址／文字生成真实二维码，可调码色和底色。占位框可用真实二维码替换。
- 设置内切换中文／English、浅色／深色／跟随系统和六种主题色。界面切换不翻译作品里的文字。

Editable text and vector shapes; precise transforms; layers and grouping; custom canvas sizes; image crops, aspect ratios and flips; color-key background removal; reusable templates and fixed brand marks; image replacement slots; three rule-based layouts; real offline QR generation; Chinese/English UI and light/dark/system appearance.

## 一个文件带走设计 / One portable file

`.zthpmsj` 是 UTF-8 JSON 容器，`format=zthpmsj`、`schema=1`，包含所有页面、对象属性、图片 data URI、默认 ZTH 黑体的 WOFF2 字节、图片槽与锁定状态。工程不引用原图路径、不依赖服务器，也没有加密。复制这一个文件到另一设备即可继续编辑；系统字体选项仍需要目标设备安装对应字体。

The UTF-8 JSON container embeds pages, object properties, image data URIs, the default WOFF2 font, replacement slots and locks. No original image path or server is required. Projects are unencrypted. Non-default system fonts require matching fonts on the destination device.

限制 / Limits: 30 pages, 2,500 objects, 60 MB input project, 24 megapixels per page; raster export up to 48 megapixels. Color removal previews at a 1,000 px longest edge and applies up to 3,000 px. Dense designs and large images may be limited by device memory.

## 兼容性 / Compatibility

| 格式 / Format | 导入 / Import | 导出 / Export |
|---|---|---|
| .zthpmsj | 完整可编辑工程 / Full editable project | 内嵌素材和默认字体 / Embedded assets and default font |
| PNG / JPG / WebP | 图片 / Image | PNG / JPG |
| SVG | 可拆分矢量组合 / Editable vector group | 矢量与内嵌图片、默认字体 / Vectors with embedded images and default font |
| PDF | 每页为图片 / One image per page | 当前页为整页图像 / Flattened current page |
| PPTX | 基础文字、照片、矩形 / Basic text, images and rectangles | 不支持 / Not supported |
| 可画 / Canva | 先从可画导出以上格式 / Export a supported format first | 不写入可画在线工程 / No Canva-native project export |

PPTX 母版、复杂形状、文字混排、动画、特效与部分字体不能保证还原。SVG 导入移除脚本、外部链接和部分动态样式。没有声称支持 PSD、AI、CDR 或可画私有工程格式的无损导入。

PPTX masters, advanced shapes, mixed text runs, animations and effects are not fully reproduced. SVG imports remove scripts and external references. There is no claimed lossless support for PSD, AI, CDR or proprietary Canva project formats.

## 升级与数据 / Upgrades and data

升级前导出工程备份。Windows 保持应用 ID、用户数据目录和安装注册项不变，关闭旧版后安装到原目录。卸载只移除程序文件；导出的文件与本地自动保存不会主动删除。Android 升级需要相同签名密钥；预览签名不能当作正式商店发布密钥。未知的未来 schema 会拒绝打开，避免静默破坏数据。

Back up before upgrading. Windows retains app identity and user data paths; close the old app and install to the same folder. Uninstall leaves projects and autosaves intact. Android upgrades require the same signing key. Unknown future schemas are rejected rather than silently rewritten.

## 构建 / Build

```sh
npm ci
npm test
npm start
```

Windows NSIS: install official NSIS 3, make `makensis` available, then `npm run build:win`. On Linux, set `ZTH_MAKENSIS` and `ZTH_NSIS_DIR` to the Linux compiler and its NSIS root. The first build downloads the pinned Electron runtime; end users do not download runtime dependencies.

Android: set `ZTH_ANDROID_PLATFORM` to Android platform 35 and `ZTH_ANDROID_BUILD_TOOLS` to build-tools 35.0.0, then `bash android/build.sh`. A JDK is recommended; the fallback accepts `ZTH_ECJ_JAR` for the Eclipse Java compiler. The script produces a development-signed APK. Keep signing keys out of Git.

Web source is in `app/`, with vendored runtime libraries for offline use. Browser ES modules and local file handling require an HTTP(S) origin; the desktop and mobile packages provide their local origin automatically. No application backend is used. `npm run build:web` creates a static copy for a suitable local host or optional static hosting.

## 验证与设计评估 / Validation

See [QA.md](QA.md) for the exact tested scope, remaining limits and design comparison. Exported samples are actual editor output, not flattened reference posters imported and presented as recreated designs. The image-generation reference was used only as a visual target; the orange geometric composition is built from editable shapes and text.

代码 MIT；品牌标识权利单独保留，见 [THIRD-PARTY.md](THIRD-PARTY.md) 和 [LICENSE](LICENSE)。

Code is MIT licensed. Brand artwork rights are reserved separately; see the attribution and third-party notices.
