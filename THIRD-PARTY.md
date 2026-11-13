# Third-party components / 第三方组件

Studio Desk original code is MIT, copyright 2026 理工阿白菌（阿白菌 / TechABJ）. The original ZTH logo and branding retain the separate rights described in ATTRIBUTION.md. Linking or publishing third-party content does not change its license.

| Component | Version | License / notice | Source |
|---|---|---|---|
| Electron | 45.3.2, Windows x64 | MIT; Chromium/Node bundled notices in LICENSE.electron.txt and LICENSES.chromium.html | https://github.com/electron/electron/releases/tag/v45.3.2 |
| CPython embeddable | 3.14.10, Windows amd64 | PSF-2.0 and bundled third-party notices in runtime/python/LICENSE.txt | https://www.python.org/downloads/release/python-31410/ |
| sharp | 0.35.5 | Apache-2.0; build-time only | https://github.com/lovell/sharp |
| rcedit | 5.0.2 | MIT; build-time only | https://github.com/electron/rcedit |
| jsdom | 30.1.3 | MIT; developer DOM tests only | https://github.com/jsdom/jsdom |
| Inno Setup | 7 | Separate official license; build compiler, not a runtime dependency | https://jrsoftware.org/isinfo.php |

Runtime versions and archive SHA-256 values are pinned in runtime-lock.json; npm build dependencies are pinned in build-runtime/package-lock.json. Official Python release and SPDX record were checked on 2026-11-06. Python archive SHA-256: 90905e64a840557d8c1bc4f5b74db3d7ee85e3ffb217611cac1c7813acea4159.

The desktop installer bundles both runtimes. It does not install a global Python, run pip, register a Python command, change PATH or depend on a machine-wide Python. Generated public sites use local HTML/CSS/assets and do not bundle the Studio Desk desktop runtime. GitHub Pages/Cloudflare documentation and network services remain subject to their own terms.

## Integrated studio modules

Desk 2 embeds Screen Studio and Forge source modules under modules/ and retains their MIT license notices. They share the Desk Electron runtime; no second installed application or hidden desktop runtime is required. Original source versions and copied files are recorded by the module provenance documentation. Forge external tools and Screen generated-firmware libraries remain governed by their own licenses and are not converted to MIT by integration.

| Three.js | 0.186.1 | MIT; notice in modules/robotics/LICENSE.three.txt | https://github.com/mrdoob/three.js |

New authored robotics course and project-route text: separate noncommercial license in modules/robotics/LICENSE-CONTENT.txt. Original procedural geometry/runtime code remain MIT. Models do not embed vendor CAD.

Academy 13 course/UI module: separate LICENSE-ZH.txt, PRIVACY-ZH.txt and third-party notices inside modules/academy. Original source HTML is identified by ORIGIN.json; source code repository https://github.com/Zeruik/zerotohand-academy. No Academy offline compiler binaries or GPL toolchain materials are duplicated in Desk.


Noto Sans SC, Copyright the Noto Project Authors, is bundled under SIL Open Font License 1.1. The unmodified font, full license and reviewed source/commit/checksums are retained in assets/fonts/. It is used locally for consistent Chinese UI and screen bitmap export; there is no font CDN.

Linux/macOS include a private CPython 3.14.10 runtime from the pinned official python-build-standalone release. Its upstream dependency license metadata and notices are retained in runtime/python/redistribution/. The optional Berkeley DB extension is excluded. Pip vendor notices remain with the runtime. This does not license the separately labelled authored Academy/robotics content under MIT.
