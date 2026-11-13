# Studio Desk 5.0.0 implementation contract

Desktop product, not a hosted website service. Local-first Windows 10/11 x64; MIT code, separate studio artwork rights. Existing Academy/Forge/Screen releases are unchanged. All runtime dependencies and writable data resolve relative to the selected installation folder, with no PATH edits. Native main/preload are product-specific. Python is bundled, isolated (`-I -B`), standard library only, invoked without shell, request JSON on stdin, response JSON on stdout.

## Current schema 2

Schema 2 retains the schema 1 fields below and adds `workspace:{brief,acceptance,bom,screen,resources}` and task `target:{kind,ref}`. New projects and native saves use producer 5.0.0. Schema 1 is accepted and migrated in memory; only a save replaces the local file after backing up its original bytes. See [API.md](API.md#integrated-desktop-apis--整合桌面接口) for field bounds, native screen/environment methods and private handoff export. Unknown/future formats fail without replacing existing data.

The task allowlist also includes `handoff`. `exportScreen` generates a separate native `screen` artifact job; it is not a Python task. Embedded modules use one shared runtime and install-relative data. Studio: 赋形造物工作室, a subsidiary of 向阳科创工作室. Creator/rightsholder: 理工阿白菌 / TechABJ. See ATTRIBUTION.md.

## Legacy schema 1 (read-only compatibility reference)
`{format:'zth-desk-project',schema:1,producer:'1.0.0',id,name,updatedAt,settings:{language:'zh'|'en',theme:'warm'|'light'|'dark',autoBuild:false},operations:{tasks:[],drafts:[]},site:{title,description,language:'zh-CN'|'en',theme:'studio'|'editorial'|'portfolio',accent:'#16806a',domain:'',basePath:'',pages:[],assets:[]}}`

- IDs: ASCII `[a-zA-Z][a-zA-Z0-9_-]{0,63}`. Project id fixed during save. All list sizes/text/assets bounded. Unknown keys rejected; future schema rejected, never silently overwritten.
- tasks `{id,title,owner,due:'YYYY-MM-DD'|'',status:'idea'|'doing'|'review'|'done',channel:'web'|'wechat'|'canva'|'event'|'other',notes}`; drafts `{id,title,body,tags:[],updatedAt}`. These are PRIVATE and never in a website/Pages commit. All optional project images require explicit site inclusion.
- pages `{id,slug:'index'|ASCII-hyphen-slug,title,nav:true,sections:[]}`; exactly one `index`. Export flat `slug.html`, relative `./assets/...`, nav relative `./slug.html`. Root/subdirectory hosting supported without SPA rewrites.
- sections `{id,type:'hero'|'text'|'cards'|'gallery'|'faq'|'cta'|'contact',title,body,image:'asset-id'|'',items:[{title,body,image:'asset-id'|'',link:''}],link:'',label:''}`. Public body is plain text with paragraphs (no arbitrary HTML/JS). Link allowed HTTPS, mailto, tel or page filename + fragment; reject javascript/data/event injection.
- assets `{id,name,mime:'image/png'|'image/jpeg'|'image/webp',data:'base64-only',alt}`. Cap 5 MiB each, 20 MiB total/project, 20 assets, validate magic bytes; dimensions can be determined client-side. No SVG import. Export from these inline bytes only, never arbitrary filesystem paths.
- domain validated hostname only (no protocol/path/credentials), normalized IDNA ASCII. basePath optional `/repo-name/`, affects sitemap/canonical URLs only; links/assets always relative.

## Renderer bridge (window.studioDesk)
All async promises; no raw filesystem or process access.
- `info()` -> `{name,version,rootDir,dataDir,pythonVersion,platform}`
- `list()` -> `[{id,name,updatedAt}]`; `load(id)` -> project; `save(project)` -> `{saved:true,id,updatedAt}` (atomic storage + bounded rotated backup)
- `importProject()` -> project|null (native file dialog, validate); `exportProject(project)` -> `{path}|null` (native save dialog)
- `run({task,project,options})` -> `{id,status:'running'}`; task allowlist `build`,`audit`,`backup`,`calendar`,`drafts`,`deploy`,`dns`.
- `job(id)` -> `{id,task,status:'running'|'done'|'failed'|'cancelled',result?,error?,startedAt,finishedAt?}`; `cancel(id)` -> state; `history()` -> compact jobs excluding tokens/private contents.
- build creates immutable `data/exports/<project-id>/<job-id>/site` and `site.zip`; result `{files:[{path,size}],siteDir,zipPath,previewHtml,report:{errors:[],warnings:[]}}`. previewHtml self-contained generated HTML, CSP for sandbox preview; no external scripts. audit returns same report without deployment.
- backup produces complete `.zthdesk` under `data/backups/`; calendar .ics and drafts Markdown under job export directory. These private outputs never become website files.
- `openOutput(jobId)` opens only actual completed output folder. `copyOutput(jobId)` native save ZIP/file dialog (copies exact artifact); `openExternal(url)` allowlisted HTTPS documentation/GitHub Pages/Cloudflare links (native confirm for arbitrary URLs).
- deploy options `{owner,repo,token,domain?,confirmPublic:true}`; token only for current invocation, stdin to Python, never saved in project/job/history/log. Native dialog confirms public file count, target repository and domain; cancel -> `{cancelled:true}`. Publish to dedicated `zth-site` branch, refuse foreign/unmarked existing branch, never touch source `main`, non-force update. Real networking only after user action. Return upload/Pages status distinctly, not 'live' until checked.
- dns options derives only site.domain; explicit user action performs DNS lookup, no automatic scanning. Report observed lookup vs configured target, cannot prove ownership/TLS propagation.

## Python engine entry
`python/worker.py` reads one JSON request from stdin <=32 MiB; `{task,project,options,outputDir}`; stdout one JSON `{ok:true,result}` or `{ok:false,error:{code,message}}`, no traceback/credentials. Main creates outputDir; Python also confines writes to this explicit output directory, no supplied file imports. `--self-test` can be supported. stdlib-only. Entry/test module importable for meaningful tests. Networking code uses validated fixed GitHub api.github.com hosts and TLS; no arbitrary request URLs from project. Deployment revision guard detects drift, cancellation best-effort (completed remote commits cannot be rolled back). No actual user-site deploy during developer tests.

## UX
Chinese/English globally, 3 themes, compact green original ZTH icon. Fixed sidebar and visible sticky actions; responsive down to 680px. Views overview / operations board+month calendar / drafts / website editor (pages/sections/inspector + sandbox live preview, mobile/desktop widths) / automation history / publish+domain / help/settings. Safe demo project from original synthetic content; explicit empty project. Images via local chooser to base64, undo/redo for editing, autosave debounced with visible state and close guard. Export whole project differs clearly from public website ZIP. No cloud account assumed. Auto-build opt-in while app open, avoid overlapping builds, stop on close; no startup task/OS scheduler. Include manual real website build/save/preview/export acceptance.
