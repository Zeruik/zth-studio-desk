'use strict';
// Synthetic service adapter: these tests cannot install, elevate, download or start WSL.
const fs=require('node:fs/promises'),os=require('node:os'),path=require('node:path'),assert=require('node:assert/strict');
const {createIntegrations}=require('./desktop/integrations.cjs');
async function main(){
 const root=await fs.mkdtemp(path.join(os.tmpdir(),'ZTH Desk Guards ')),calls=[],checks=[];let response=0,config;
 const plan={id:'plan-synthetic',options:{task:'wsl'},steps:[{kind:'wsl',title:'Fixture only'}]};
 const facade=await createIntegrations({root,win:{},dialog:{showMessageBox:async()=>({response})},createForge:c=>{config=c;return{catalog:()=>({fixture:true}),getPlan:()=>plan,job:()=>({id:'job-synthetic',plan}),activeJob:()=>null,start:async(...a)=>{calls.push(['start',...a]);return{jobId:'job-synthetic'};},resume:async(...a)=>{calls.push(['resume',...a]);return{jobId:'job-synthetic'};},deepDetect:async(...a)=>{calls.push(['deepDetect',...a]);return{fixture:true};}};}});
 assert.equal(config.appDataDir,path.join(root,'data/environment'));
 assert.deepEqual(await facade.forge('catalog'),{fixture:true});
 for(const method of ['exec','shell','constructor','__proto__'])await assert.rejects(facade.forge(method),/ENVIRONMENT_CALL_INVALID/);
 await assert.rejects(facade.forge('start','plan-synthetic',{confirmed:true}),/ENVIRONMENT_CALL_INVALID/);checks.push('Only allowlisted calls with one bounded argument cross the native facade');
 for(const method of ['start','deepDetect'])assert.deepEqual(await facade.forge(method,method==='deepDetect'?'ZTH-Synthetic':'plan-synthetic'),{cancelled:true});
 await assert.rejects(facade.forge('resume','unknown-job'),/PLAN_NOT_FOUND/);
 assert.equal(calls.length,0);checks.push('Cancellation stops install, resume and distro startup before invoking the service');
 response=1;await facade.forge('start','plan-synthetic');response=0;assert.deepEqual(await facade.forge('resume','job-synthetic'),{cancelled:true});assert.equal(calls.length,1);response=1;await facade.forge('resume','job-synthetic');await facade.forge('deepDetect','ZTH-Synthetic');
 assert.deepEqual(calls[0],['start','plan-synthetic',{confirmed:true}]);assert.deepEqual(calls[1],['resume','job-synthetic',{confirmed:true}]);assert.deepEqual(calls[2],['deepDetect','ZTH-Synthetic']);checks.push('Native approval supplies confirmation; the renderer cannot supply it');
 const linked=path.join(root,'Linked'),outside=path.join(root,'Outside');await fs.mkdir(path.join(linked,'data'),{recursive:true});await fs.mkdir(outside);await fs.symlink(outside,path.join(linked,'data/environment'),'junction');await assert.rejects(createIntegrations({root:linked,dialog:{},createForge:()=>{throw Error('MUST_NOT_START');}}),/UNSAFE_ENVIRONMENT_DIRECTORY/);assert.deepEqual(await fs.readdir(outside),[]);checks.push('Environment storage cannot escape through a junction');
 const report=path.resolve(process.argv[2]||path.join(__dirname,'qa-output/native-guards.json'));await fs.mkdir(path.dirname(report),{recursive:true});await fs.writeFile(report,JSON.stringify({passed:true,checks,scope:'Synthetic service adapter; no real installation or system changes.'},null,2));console.log('PASS '+checks.length+' native integration guards');
}
main().catch(e=>{console.error(e.stack);process.exitCode=1;});
