# 验证与评估 / Validation and assessment

Date: 2026-11-13. Preview 1.0.0. Tests describe observed outcomes, not certification of every machine or source format.

| 检查 / Check | 结果 / Result |
|---|---|
| Connected color removal / 连通抠色 | Unit test passes; a light-green test background was clicked and became transparent while white interior details remained. |
| Tolerance and edge softness / 容差与柔化 | Numerical tests pass; source pixels are not mutated. |
| Portable-project validation / 原生工程校验 | Embedded images accepted; external image URLs, future schemas, invalid types and excessive dimensions rejected. |
| Layout / 自动排版 | Three layouts keep a representative logo, heading, photos, body and QR inside canvas bounds. Dense designs still need review. |
| Templates / 内置模板 | 17 editable templates including palette variants; text and shape objects remain separate. |
| PNG export / PNG导出 | Actual editor output checked at 1080×1440, 1080×1800 and 1440×1440. |
| PDF export / PDF导出 | Actual output inspected: one page containing the expected flattened image. |
| PDF import / PDF导入 | A real single-page PDF was rendered and added as a new image page. |
| PPTX import / PPTX导入 | A synthetic basic slide imported as editable text. This does not establish fidelity for arbitrary PowerPoint decks. |
| SVG import / SVG导入 | A rectangle/circle/text fixture imported as an editable group. |
| Native round trip / 工程回读 | An exported .zthpmsj was re-imported and restored its 31 editable objects. |
| QR / 二维码 | A real URL QR was generated in the editor and placed into a recruitment template. OpenCV decoded the final exported PNG as https://github.com/Zeruik. |
| Brand consistency / 品牌一致性 | Two editor-saved projects compared byte-for-byte: replacement changed the product pixels while logo bytes, locks, location, rotation, frame size and object order stayed fixed. See qa/brand-consistency.json. |
| Shape authoring / 元素创建 | A rectangle was added through the UI, made 400×400 px, rotated 30°, moved to (220,220) and filled orange using the property panel. |
| Custom templates / 自定义模板 | Saved to My Templates; remained present after page reload. Export uses the same self-contained native format. |
| UI language / 双语界面 | Chinese → English → Chinese tested; project wording preserved. Dynamic user layer names are intentionally not translated. |
| Appearance / 外观 | Dark/light choices tested; system-mode listener and six accent colors implemented. |
| Mobile layout / 手机布局 | The same app was exercised in a real 390×844 iframe viewport; tool navigation and the property drawer worked. This is not a physical-phone test. |
| Android package / 安卓包 | APK compilation and Android signature verification passed. Native file picker/save and device gestures still require physical-device acceptance. |
| Windows package / Windows包 | Native NSIS installer compiled with language, license, path, shortcuts, file association and uninstaller. No Windows machine was online, so actual installation/uninstallation is unverified. |

## 设计对照 / Design comparison

The generated orange editorial poster served as a visual target. The editor version was rebuilt with a separate text hierarchy, guide lines, a circle and individually editable orange vector bands. It does not use the generated poster as a flattened background. Compared with the first editor version, headline size, hero scale and footer hierarchy were increased; internal band stacking and the guide-circle margin were corrected. Subjective assessment: the style is now recognizably similar, while the reference's optical geometry remains more refined. This is not claimed as visual parity or the user's final design approval.

The content-rich recruitment example uses editable headings, six separate information cards, typography, geometric color ribbons, an embedded original logo crop, generated workshop photography and a real QR. The lower photograph was moved into its own column after the first export made text sit on a busy photo. It captures the reference's green/blue information hierarchy while using a more restrained layout; brush textures and decorative lettering have not been replicated.

The product template demonstrates a reusable brand system rather than a one-off poster: the actual supplied studio mark is color-keyed by the app, locked above the product image and preserved during replacement. Product photography is an image asset; title, footer, logo and frame are separate objects.

## 未完成的验收 / Remaining acceptance

- Physical Windows install, path selection, launch, file association, upgrade and uninstall.
- Physical Android install, file picker/save, touch transforms and cross-device .zthpmsj round trip.
- Broader source-format fixtures for complex PPTX, real-world PDFs and SVG edge cases.
- Further visual refinement of the dense recruitment posters to the user's reference standard. The preview is not described as a mature Canva-equivalent release.
