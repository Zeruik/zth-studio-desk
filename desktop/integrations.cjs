'use strict';
// Product-owned native integration. The renderer never chooses a command or executable.
const fs=require('node:fs/promises'),path=require('node:path');
const {createForgeService}=require('../modules/forge/backend.cjs');
const ALLOWED=new Set(['catalog','history','detect','deepDetect','createPlan','getPlan','exportPlan','start','cancel','resume','job','selectDirectory','selectRootfs','importCache']);
async function safeDirectory(root,relative){let at=root;for(const part of relative.split('/')){at=path.join(at,part);await fs.mkdir(at,{recursive:true});const s=await fs.lstat(at);if(s.isSymbolicLink()||!s.isDirectory())throw Error('UNSAFE_ENVIRONMENT_DIRECTORY');}return at;}
async function createIntegrations({root,win,dialog,sendProgress=()=>{},createForge=createForgeService}){
 const dataDir=await safeDirectory(root,'data/environment');
 const title='赋形造物工作台 · ZTH Studio Desk';
 const service=createForge({appDataDir:dataDir,sendProgress,dialogs:{
  selectDirectory:async()=>{const r=await dialog.showOpenDialog(win,{title:'选择工程环境目录 / Choose environment directory',properties:['openDirectory','createDirectory']});return r.canceled?null:r.filePaths[0];},
  selectRootfs:async()=>{const r=await dialog.showOpenDialog(win,{title:'选择已有 Ubuntu rootfs / Choose an existing rootfs',properties:['openFile'],filters:[{name:'Ubuntu rootfs',extensions:['tar','gz','wsl']}]});return r.canceled?null:r.filePaths[0];},
  savePlan:async({filename,script})=>{const r=await dialog.showSaveDialog(win,{title:'导出待审阅脚本 / Export a script for review',defaultPath:filename,filters:[{name:'PowerShell script',extensions:['ps1']}]});if(r.canceled)return null;await fs.writeFile(r.filePath,script,'utf8');return{path:r.filePath};}
 }});
 let confirming=false;const jobPlans=new Map();
 async function confirm(message,detail,action){const r=await dialog.showMessageBox(win,{type:'warning',title,buttons:['取消 / Cancel',action],defaultId:0,cancelId:0,noLink:true,message,detail});return r.response===1;}
 async function forge(method,...args){
  if(!ALLOWED.has(method)||args.length>1||Buffer.byteLength(JSON.stringify(args),'utf8')>65536)throw Error('ENVIRONMENT_CALL_INVALID');
  if(['start','resume','deepDetect'].includes(method)){
   if(confirming)throw Error('CONFIRMATION_BUSY');confirming=true;
   try{
    if(method==='deepDetect'){
     if(typeof args[0]!=='string'||args[0].length>64)throw Error('DISTRO_INVALID');
     if(!await confirm('启动此 WSL 发行版并读取版本信息？ / Start this WSL distro to inspect versions?',args[0]+'\n只读取系统、ROS 和编译器信息；可能启动已停止的发行版。\nReads OS, ROS and compiler versions; a stopped distro may start.','读取信息 / Inspect'))return{cancelled:true};
     return await service.deepDetect(args[0]);
    }
    if(typeof args[0]!=='string'||args[0].length>128)throw Error('PLAN_INVALID');
    const plan=method==='start'?service.getPlan(args[0]):jobPlans.get(args[0]);
    if(!plan)throw Error('PLAN_NOT_FOUND');
    const detail=JSON.stringify({task:plan.options?.task,target:plan.options?.location||'',distro:plan.options?.distro||'',steps:plan.steps},null,2).slice(0,14000)+'\n\n这会下载或安装第三方工程环境，可能修改 Windows 功能。部分安装需要管理员权限或之后手动重启。不会自动重启；取消不能撤销已完成步骤。\nThis changes the computer: third-party downloads/installation and possibly Windows features. Administrator access or a later manual restart may be required. No automatic restart or rollback. Imported projects never execute a plan automatically.';
    if(!await confirm('执行已审阅的工程环境计划？ / Execute the reviewed environment plan?',detail,method==='resume'?'继续执行 / Resume':'执行计划 / Execute'))return{cancelled:true};
    const result=await service[method](args[0],{confirmed:true});
    if(method==='start'&&result?.jobId)jobPlans.set(result.jobId,plan);
    return result;
   }finally{confirming=false;}
  }
  return service[method](...args);
 }
 return{forge,activeJob:()=>service.activeJob(),cancel:id=>service.cancel(id),dataDir};
}
module.exports={createIntegrations,ALLOWED};
