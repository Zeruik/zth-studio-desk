'use strict';
const {contextBridge,ipcRenderer}=require('electron');
const api={};
for(const name of ['info','list','load','save','importProject','exportProject','run','job','cancel','history','openOutput','copyOutput','openExternal','forge','exportScreen'])api[name]=(...args)=>ipcRenderer.invoke('desk:'+name,...args);
api.onForgeProgress=fn=>{if(typeof fn!=='function')throw Error('CALLBACK_REQUIRED');const listener=(_event,value)=>fn(value);ipcRenderer.on('desk:forge-progress',listener);return()=>ipcRenderer.removeListener('desk:forge-progress',listener);};
contextBridge.exposeInMainWorld('studioDesk',Object.freeze(api));
