'use strict';
(function(){
const $=id=>document.getElementById(id),E=ZTH_EDITOR,F=fabric;let templates=[],replacement=null;
const ready=E.dbGet('userTemplates').then(v=>{templates=Array.isArray(v)?v:[];}).catch(()=>{});
function capture(){const d=JSON.parse(JSON.stringify(E.getProject()));d.kind='template';d.name=$('templateName').value.trim();return d;}
function openSave(){if(!$('templateName').value)$('templateName').value=$('projectName').value;$('templateDialog').showModal();}
$('saveUserTemplate').onclick=async()=>{if(!$('templateName').value.trim())return E.toast('请填写模板名称');const doc=capture(),thumb=E.canvas.toDataURL({format:'png',multiplier:Math.min(1,240/E.canvas.getWidth())});const item={id:'user-'+Date.now(),name:doc.name,category:'我的模板',document:doc,thumb};templates.push(item);try{await E.dbPut('userTemplates',templates);$('templateDialog').close();E.openTab('templates');E.toast('模板已保存到此设备');}catch{templates.pop();E.toast('模板保存失败，请导出模板备份');}};
$('exportUserTemplate').onclick=async()=>{if(!$('templateName').value.trim())return E.toast('请填写模板名称');const doc=capture(),name=doc.name.replace(/[\\/:*?"<>|]/g,'-');await E.download(new Blob([JSON.stringify(doc)],{type:'application/json'}),name+'.zthpmsj');$('templateDialog').close();};
$('replaceImageBtn').onclick=()=>{replacement=E.canvas.getActiveObject();if(replacement?.type!=='image')return E.toast('先添加图片，再设为图片槽。');$('replaceImageInput').click();};
async function replaceWithFile(file,o){if(!file||!o)return;if(o.locked)return E.toast('请先解锁该元素');try{if(file.size>25e6)throw Error('单张图片请小于 25 MB');let url=await new Promise((resolve,reject)=>{const r=new FileReader();r.onload=()=>resolve(r.result);r.onerror=reject;r.readAsDataURL(file);});const test=new Image();test.src=url;await test.decode();if(test.naturalWidth*test.naturalHeight>24000000)throw Error('单张图片请小于 2400 万像素');const fw=o.width*o.scaleX,fh=o.height*o.scaleY;await o.setSrc(url);let sc=Math.max(fw/o.width,fh/o.height),cw=fw/sc,ch=fh/sc;o.set({cropX:(o.width-cw)/2,cropY:(o.height-ch)/2,width:cw,height:ch,scaleX:sc,scaleY:sc});o.setCoords();E.canvas.requestRenderAll();E.changed();E.toast('图片已替换，品牌与版式保持原位');}catch(err){E.toast(err.message);}}
$('replaceImageInput').onchange=async e=>{const f=e.target.files[0];e.target.value='';await replaceWithFile(f,replacement);};

$('imageSlot').onchange=()=>{const o=E.canvas.getActiveObject();if(!o)return;o.imageSlot=$('imageSlot').checked;if(o.imageSlot)o.role='photo';E.changed();};$('keepRatio').onchange=()=>{const o=E.canvas.getActiveObject();if(!o)return;o.keepRatio=$('keepRatio').checked;E.changed();};
window.ZTH_TEMPLATE={ready,openSave,replaceWithFile,list:()=>templates,remove:async id=>{templates=templates.filter(t=>t.id!==id);await E.dbPut('userTemplates',templates);E.openTab('templates');}};
})();
