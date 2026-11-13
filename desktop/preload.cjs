const {contextBridge,ipcRenderer}=require('electron');
contextBridge.exposeInMainWorld('zthDesktop',{ready:()=>ipcRenderer.send('zth:ready'),font:()=>ipcRenderer.invoke('zth:font'),onProject:cb=>ipcRenderer.on('zth:project',(_,text)=>cb(text)),save:p=>ipcRenderer.invoke('zth:save',p),environment:()=>ipcRenderer.invoke('zth:environment')});
