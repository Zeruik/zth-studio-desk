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
