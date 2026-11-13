const {spawnSync}=require('node:child_process');
const path=require('node:path'),fs=require('node:fs');
function run(cmd,args,opts={}){const r=spawnSync(cmd,args,{stdio:'inherit',...opts});if(r.status!==0)process.exit(r.status||1);}
run(process.execPath,['node_modules/electron-builder/cli.js','--win','--x64','--dir','--publish','never']);
const root=path.resolve('release/win-unpacked'),entries=[];
function walk(dir){
 for(const n of fs.readdirSync(dir)){
  const p=path.join(dir,n),rel=path.relative(root,p).replaceAll(path.sep,'\\');
  if(fs.statSync(p).isDirectory()){walk(p);entries.push('RMDir "$INSTDIR\\'+rel+'"');}
  else entries.push('Delete "$INSTDIR\\'+rel+'"');
 }
}
walk(root);
entries.push('Delete "$INSTDIR\\icon.ico"','Delete "$INSTDIR\\Uninstall.exe"','RMDir "$INSTDIR"');
fs.writeFileSync('build/uninstall-files.nsh',entries.join('\n')+'\n');
const nsis=process.env.ZTH_MAKENSIS||'makensis';
const env={...process.env};
if(process.env.ZTH_NSIS_DIR)env.NSISDIR=process.env.ZTH_NSIS_DIR;
run(nsis,['installer.nsi'],{cwd:path.resolve('build'),env});
