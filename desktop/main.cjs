'use strict';
// Product-owned desktop shell. All application state follows the chosen install path.
const {app,BrowserWindow,Menu,ipcMain,session,dialog,shell,protocol,net}=require('electron');
protocol.registerSchemesAsPrivileged([{scheme:'zthdesk',privileges:{standard:true,secure:true,supportFetchAPI:true,corsEnabled:true}}]);
const path=require('node:path'),fs=require('node:fs'),{pathToFileURL}=require('node:url');
const config=require('../product.json'),{createDeskService}=require('../backend.cjs'),{createIntegrations}=require('./integrations.cjs');
for(const stream of [process.stdout,process.stderr])stream?.on('error',e=>{if(e.code!=='EPIPE')throw e;});
const root=app.isPackaged?path.dirname(process.execPath):path.join(app.getAppPath(),'.desk-dev');
try{fs.mkdirSync(root,{recursive:true});for(const sub of ['','desktop','browser','logs','crash','tmp']){const dir=path.join(root,'data',sub);fs.mkdirSync(dir,{recursive:true});if(fs.lstatSync(dir).isSymbolicLink()||!fs.lstatSync(dir).isDirectory())throw Error('UNSAFE_DATA_DIRECTORY');}
 app.setName(config.name);app.setAppUserModelId(config.id);app.setPath('userData',path.join(root,'data','desktop'));app.setPath('sessionData',path.join(root,'data','browser'));app.setPath('logs',path.join(root,'data','logs'));app.setPath('crashDumps',path.join(root,'data','crash'));app.setPath('temp',path.join(root,'data','tmp'));process.env.TEMP=path.join(root,'data','tmp');process.env.TMP=process.env.TEMP;
}catch{dialog.showErrorBox(config.name,'所选安装目录无法写入，请选择自己有写入权限的英文目录。资料不会自动转移到 C 盘。\nThe installation folder must be writable; no alternate data folder was used.');app.exit(1);}
const entry=path.join(__dirname,'..','index.html'),entryUrl='zthdesk://app/index.html';let win,service,integrations;
function trusted(e){return !!win&&!win.isDestroyed()&&e.sender===win.webContents&&e.senderFrame===win.webContents.mainFrame&&e.senderFrame.url.split('#')[0]===entryUrl;}
function handle(name,fn){ipcMain.handle('desk:'+name,async(e,...args)=>{if(!trusted(e))throw Error('UNTRUSTED_SENDER');return fn(...args);});}
async function external(raw){if(typeof raw!=='string'||raw.length>2048)throw Error('URL_INVALID');let u;try{u=new URL(raw);}catch{throw Error('URL_INVALID');}if(u.username||u.password)throw Error('URL_INVALID');if(u.protocol==='mailto:'&&u.pathname==='zeruik@qq.com'){await shell.openExternal(u.href);return true;}if(u.protocol!=='https:')throw Error('HTTPS_REQUIRED');const hosts=['github.com','docs.github.com','developers.cloudflare.com','dash.cloudflare.com','www.python.org','docs.python.org'];if(!hosts.includes(u.hostname)&&!u.hostname.endsWith('.github.io')&&!u.hostname.endsWith('.pages.dev')){const r=await dialog.showMessageBox(win,{type:'question',title:config.name,buttons:['取消 / Cancel','打开浏览器 / Open browser'],defaultId:0,cancelId:0,message:'打开这个外部网站？ / Open this external website?',detail:u.href});if(r.response!==1)return false;}await shell.openExternal(u.href);return true;}
if(!app.requestSingleInstanceLock())app.quit();else{
 app.on('second-instance',()=>{if(win){if(win.isMinimized())win.restore();win.show();win.focus();}});
 app.whenReady().then(async()=>{
  const contentRoot=path.resolve(__dirname,'..');
  protocol.handle('zthdesk',async request=>{const u=new URL(request.url);let relative;try{relative=decodeURIComponent(u.pathname);}catch{return new Response('Invalid path',{status:400});}if(u.hostname!=='app'||request.method!=='GET'||relative.includes('\\')||relative.includes('\0'))return new Response('Forbidden',{status:403});const target=path.resolve(contentRoot,'.'+relative);if(!target.startsWith(contentRoot+path.sep))return new Response('Forbidden',{status:403});try{if(!fs.statSync(target).isFile())return new Response('Not found',{status:404});return await net.fetch(pathToFileURL(target).href);}catch{return new Response('Not found',{status:404});}});
  Menu.setApplicationMenu(null);session.defaultSession.setPermissionRequestHandler((_w,_p,reply)=>reply(false));session.defaultSession.setPermissionCheckHandler(()=>false);
  const csp="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; font-src 'self' data:; connect-src zthdesk://app; frame-src 'self' data: blob:; object-src 'none'; base-uri 'none'";
  session.defaultSession.webRequest.onHeadersReceived((details,reply)=>reply({responseHeaders:{...details.responseHeaders,'Content-Security-Policy':[csp]}}));
  win=new BrowserWindow({width:1460,height:960,minWidth:680,minHeight:560,show:false,backgroundColor:config.background||'#f6f3eb',icon:path.join(__dirname,'icon.ico'),webPreferences:{preload:path.join(__dirname,'preload.cjs'),sandbox:true,contextIsolation:true,nodeIntegration:false,nodeIntegrationInSubFrames:false,webSecurity:true}});
  win.once('ready-to-show',()=>win.show());
  win.webContents.setWindowOpenHandler(({url})=>{void external(url).catch(()=>{});return{action:'deny'};});
  win.webContents.on('will-navigate',(event,url)=>{if(url.split('#')[0]!==entryUrl){event.preventDefault();void external(url).catch(()=>{});}});
  win.webContents.on('will-attach-webview',event=>event.preventDefault());
  win.webContents.on('will-prevent-unload',event=>{const choice=dialog.showMessageBoxSync(win,{type:'question',title:config.name,buttons:['返回保存 / Return to save','舍弃未保存修改 / Discard changes'],defaultId:0,cancelId:0,message:'还有未保存的修改。Unsaved changes remain.'});if(choice===1)event.preventDefault();});
  win.on('close',event=>{const job=service?.activeJob(),environment=integrations?.activeJob();if(!job&&!environment)return;event.preventDefault();const choice=dialog.showMessageBoxSync(win,{type:'warning',title:config.displayName||config.name,buttons:['继续等待 / Keep open','取消任务 / Cancel task'],defaultId:0,cancelId:0,message:'任务仍在运行，请等待或先取消。A task is still running.',detail:'已完成的远端发布或系统安装不会因取消而撤销。系统安装步骤会等待结束。\nCompleted remote changes and installation steps are not rolled back. A running system installer may need to finish.'});if(choice===1){if(job)void service.cancel(job.id).catch(()=>{});if(environment)void integrations.cancel(environment.id).catch(()=>{});}});
  const python=app.isPackaged?path.join(root,'runtime','python','python.exe'):path.join(app.getAppPath(),'runtime','python','python.exe');
  service=createDeskService({rootDir:root,pythonExecutable:python,workerPath:path.join(__dirname,'..','python','worker.py'),dialogs:{
   openProject:async()=>{const r=await dialog.showOpenDialog(win,{properties:['openFile'],filters:[{name:'ZTH Desk project',extensions:['zthdesk']}]});return r.canceled?null:r.filePaths[0];},
   saveProject:async({filename})=>{const r=await dialog.showSaveDialog(win,{defaultPath:filename,filters:[{name:'ZTH Desk project',extensions:['zthdesk']}]});return r.canceled?null:r.filePath;},
   saveArtifact:async({filename})=>{const r=await dialog.showSaveDialog(win,{defaultPath:filename});return r.canceled?null:r.filePath;},
   openPath:async target=>{const error=await shell.openPath(target);if(error)throw Error('OPEN_FOLDER_FAILED');},
   confirmDeploy:async({owner,repo,domain,pages,images})=>{const r=await dialog.showMessageBox(win,{type:'warning',title:config.name,buttons:['取消 / Cancel','公开发布网站 / Publish website'],defaultId:0,cancelId:0,noLink:true,message:'把网站内容发布到 GitHub Pages？Publish this website to GitHub Pages?',detail:`Repository: ${owner}/${repo}\nBranch: zth-site\nPages: ${pages} · Images: ${images}\nDomain: ${domain||'(GitHub default)'}\n\n网站文案和图片将公开；运营任务与私有草稿不上传。令牌只用于本次请求。请先在预览中检查公开内容。\nSite text and images become public. Private operations/drafts are excluded. The token is only used for this request. DNS and HTTPS may need separate configuration.`});return r.response===1;}
  }});
  await service.init();
  integrations=await createIntegrations({root,win,dialog,sendProgress:event=>{if(win&&!win.isDestroyed())win.webContents.send('desk:forge-progress',event);}});
  handle('info',()=>({name:config.name,displayName:config.displayName||config.name,version:config.version,studio:config.studio,parentStudio:config.parentStudio,creator:config.creator,bioZh:config.bioZh,bioEn:config.bioEn,rootDir:root,dataDir:service.paths.data,pythonVersion:config.pythonVersion||'3.14.10',pythonReady:fs.existsSync(python),platform:process.platform}));
  for(const name of ['list','load','save','importProject','exportProject','run','job','cancel','history','openOutput','copyOutput'])handle(name,(...args)=>service[name](...args));
  handle('forge',(...args)=>integrations.forge(...args));handle('exportScreen',request=>service.exportScreen(request));
  handle('openExternal',external);await win.loadURL(entryUrl);
 }).catch(error=>{dialog.showErrorBox(config.name,'启动未完成 / Startup could not finish\n'+String(error.code||error.message));app.quit();});
 app.on('window-all-closed',()=>app.quit());
}
