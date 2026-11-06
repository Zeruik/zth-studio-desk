'use strict';
const {contextBridge,ipcRenderer}=require('electron');
const api={};
for(const name of ['info','list','load','save','importProject','exportProject','run','job','cancel','history','openOutput','copyOutput','openExternal'])api[name]=(...args)=>ipcRenderer.invoke('desk:'+name,...args);
contextBridge.exposeInMainWorld('studioDesk',Object.freeze(api));
