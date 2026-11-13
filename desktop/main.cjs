const {app,BrowserWindow,ipcMain,dialog,shell,session}=require('electron');
const path=require('node:path'),fs=require('node:fs/promises'),os=require('node:os');
let win;let pendingFile=process.argv.find(a=>a.toLowerCase().endsWith('.zthpmsj'));
async function openProject(p){if(!p)return;try{const stat=await fs.stat(p);if(stat.size>60*1024*1024)throw Error('工程超过 60 MB');const text=await fs.readFile(p,'utf8');win.webContents.send('zth:project',text);}catch(e){dialog.showErrorBox('打开工程失败',e.message);}}
app.setName('ZTH-平面设计器');
if(!app.requestSingleInstanceLock()){app.quit();}else{
app.on('second-instance',(_,argv)=>{if(win){win.restore();win.focus();openProject(argv.find(a=>a.toLowerCase().endsWith('.zthpmsj')));}});
app.whenReady().then(async()=>{
 const prefs={preload:path.join(__dirname,'preload.cjs'),nodeIntegration:false,contextIsolation:true,sandbox:true,webSecurity:true};
 win=new BrowserWindow({width:1480,height:980,minWidth:760,minHeight:620,backgroundColor:'#f7f6f9',title:'ZTH-平面设计器',icon:path.join(__dirname,'../app/assets/app-icon.png'),webPreferences:prefs});
 win.setMenuBarVisibility(false);win.webContents.setWindowOpenHandler(()=>({action:'deny'}));
 win.webContents.on('will-navigate',(e,url)=>{if(!url.startsWith('file://'))e.preventDefault();});
 session.defaultSession.setPermissionRequestHandler((_,__,cb)=>cb(false));
 
 await win.loadFile(path.join(__dirname,'../app/index.html'));
 let errors=[];if(process.platform==='win32'&&Number(os.release().split('.')[0])<10)errors.push('需要 Windows 10 或更新版本');
 try{let p=path.join(app.getPath('userData'),'.write-test');await fs.writeFile(p,'ok');await fs.unlink(p);}catch{errors.push('用户数据目录无法写入，请使用可写用户账户');}
 if(errors.length)dialog.showMessageBox(win,{type:'warning',title:'环境检查',message:errors.join('\n')});
});
}
ipcMain.on('zth:ready',e=>{if(e.sender===win?.webContents&&pendingFile){openProject(pendingFile);pendingFile=null;}});
ipcMain.handle('zth:save',async(e,p)=>{if(e.sender!==win?.webContents||!p||typeof p.name!=='string'||!p.bytes||p.bytes.length>250*1024*1024)throw Error('无效的导出请求');let name=path.basename(p.name).replace(/[<>:"/\\|?*]/g,'-');if(!/\.(zthpmsj|png|jpg|svg|pdf)$/.test(name))throw Error('不支持的文件格式');let result=await dialog.showSaveDialog(win,{defaultPath:name});if(result.canceled)return false;await fs.writeFile(result.filePath,Buffer.from(p.bytes));return true;});
ipcMain.handle('zth:font',async()=> 'data:font/woff2;base64,'+(await fs.readFile(path.join(__dirname,'../app/assets/fonts/ZTHSans.woff2'))).toString('base64'));
ipcMain.handle('zth:environment',()=>`${process.platform} ${os.release()} · ${os.arch()} · 内存 ${Math.round(os.totalmem()/1024**3)} GB · Electron ${process.versions.electron} · 应用 ${app.getVersion()} · 本地运行时已内置`);
app.on('window-all-closed',()=>app.quit());
