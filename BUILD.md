# Reproduce Studio Desk 2.0.0

Build on Windows 10/11 x64 with Node.js 22.22.2 or later and official Inno Setup 7. These are developer tools; end users need neither Node nor Python installed.

1. In build-runtime/, run npm ci. This downloads the pinned Electron/sharp/rcedit/jsdom development dependencies.
2. Return to the product directory and run node prepare-runtime.cjs. It downloads the official CPython embeddable archive to excluded .cache/, checks runtime-lock.json SHA-256 and checks every extracted file. No global Python is registered and no pip runs.
3. Run node build-release.cjs. Set ZTH_ISCC for a nonstandard Inno compiler path. Optional process-only ZTH_BUILD_MODULES, ZTH_RUNTIME_CACHE and ZTH_ELECTRON_ZIP can select existing verified build inputs. No environment variable needs to be set permanently.

Outputs are out/build/studio-desk, out/source/zth-studio-desk-v2 and out/release/ZTH-Studio-Desk-Windows-v2.0.0.zip. The builder refuses pre-existing output folders. Preserve old outputs and select a new output root in the buildProduct API; it never recursively erases them.

Runtime archives are pinned by official release SHA-256. The Electron archive is located in its download cache or downloaded from its official release; every stock runtime file is compared before branding. Python is copied exactly from its checked archive, including PSF and dependency licenses. Both runtimes remain inside the selected installed folder. Runtime files, private data, caches and toolchains do not enter the public source repository.

Public files use an explicit allowlist. SOURCE-MANIFEST.json covers all source files except itself; PACKAGE-MANIFEST.json covers every installed payload file before user data is created. .gitattributes disables automatic newline conversion so Git blobs match source hashes. .gitignore is additional protection, not the publication boundary.

Setup is unsigned and includes its runtimes for offline launch. Application publishing/DNS remain intentionally networked actions. License notices must be retained. This builder does not deploy a website or install the application.

## Storage and upgrades

All data lives in data/ beside the executable, including projects, exports, backups, browser storage and job records. Choose an English path writable by the account that will run the application; spaces are supported. Windows/Program Files and paths through junctions or symlinks are blocked. A folder writable only by another account is unsuitable.

Use the same folder for upgrades. Before changing folders, launch the old application once, close it normally, then COPY the complete folder including data/ to the new location. Keep the original readable until Setup finishes. Setup compares both data/installation-id.json markers and refuses unverified relocation. It never copies or deletes your old data itself. Do not copy only the EXE. Stable AppId and product identity are kept for upgrades; downgrades and installation while the app is running are blocked.

Uninstall removes tracked program/runtime files and retains data/. Export important .zthdesk backups before updates or manual cleanup. Setup does not edit PATH or register Python, so there is no PATH change to reverse. Existing external sites are independent of uninstall.

## Focused checks

Run node qa-backend.cjs and the engine tests described in README.md with the bundled Python. node qa-runtime.cjs exercises empty child PATH and copied relative storage. node qa-installer.cjs builds and installs a tiny random-AppId fixture; after a build set process-only ZTH_QA_ICON to out/build/studio-desk/icon.ico. Its synthetic folders are isolated and removed; logs remain in excluded qa-output/. These checks do not publish a real site.

Renderer/core checks: run node qa-core.cjs. For standalone source DOM checks, run node -e "process.env.ZTH_JSDOM_MODULE=require.resolve('./build-runtime/node_modules/jsdom/lib/api.js');require('./qa-ui.cjs')". JSDOM is pinned at 30.1.3 as a developer-only dependency and is not copied into the application.

## Brand and version identity

Additional integrated checks: `node qa-native-guards.cjs` and `node qa-project-v2.cjs <absolute-path-to-bundled-python.exe>`. These use synthetic projects; the native guard test replaces the environment service and performs no system installation. Source documentation can advance after a release: use the tagged source for an exact installer snapshot, and verify its SOURCE-MANIFEST.json. Documentation-only commits do not replace historical release ZIPs or their checksums.

Product name: 赋形造物工作台 / ZTH Studio Desk. Studio: 赋形造物工作室, a subsidiary of 向阳科创工作室. Creator/rightsholder: 理工阿白菌（阿白菌 / TechABJ）. Public Git identity remains Zeruik with a GitHub noreply address. Stable AppId, executable and installation folder are unchanged from Desk 1; do not regenerate them for updates. MIT code and separately reserved original artwork rights are described in LICENSE and ATTRIBUTION.md.
