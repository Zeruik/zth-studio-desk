import * as pdfjs from './vendor/pdf.mjs';
pdfjs.GlobalWorkerOptions.workerSrc=new URL('./vendor/pdf.worker.mjs',import.meta.url).href;
const E=window.ZTH_EDITOR,F=window.fabric;
const xml=s=>{let d=new DOMParser().parseFromString(s,'application/xml');if(d.querySelector('parsererror'))throw Error('无效的 Office XML');return d;};
const nodes=(n,tag)=>Array.from(n.getElementsByTagNameNS('*',tag));
const first=(n,tag)=>nodes(n,tag)[0];
const attr=(n,a,fallback=0)=>Number(n?.getAttribute(a)||fallback);
async function pdf(file){
 E.toast('正在本地读取 PDF…');let doc=await pdfjs.getDocument({data:new Uint8Array(await file.arrayBuffer()),isEvalSupported:false,useSystemFonts:true}).promise;
 if(doc.numPages>20)throw Error('PDF 最多导入 20 页，请先拆分');
 for(let i=1;i<=doc.numPages;i++){let page=await doc.getPage(i),v=page.getViewport({scale:1}),scale=Math.min(2,2400/Math.max(v.width,v.height));v=page.getViewport({scale});let c=document.createElement('canvas');c.width=Math.round(v.width);c.height=Math.round(v.height);if(c.width*c.height>12000000)throw Error('PDF 页面尺寸过大');await page.render({canvasContext:c.getContext('2d'),viewport:v}).promise;let img=await F.FabricImage.fromURL(c.toDataURL('image/png'));img.set({name:'PDF 第 '+i+' 页（整页图像）',role:'photo'});await E.addImportedPage({width:c.width,height:c.height,canvas:{background:'#ffffff',objects:[img.toObject()]}});page.cleanup();}
 await doc.destroy();E.toast('PDF 已按页导入为图像；可继续叠加文字与素材');
}
async function pptx(file){
 E.toast('正在解析 PPTX 基础元素…');let zip=await JSZip.loadAsync(await file.arrayBuffer());let expanded=0;for(const f of Object.values(zip.files)){const n=f._data?.uncompressedSize||0;if(n>25000000)throw Error('PPTX 内部文件过大');expanded+=n;if(expanded>150000000)throw Error('PPTX 解压后超过 150 MB');}let files=Object.keys(zip.files);if(files.length>5000)throw Error('PPTX 项目过多');let entries=files.filter(p=>/^ppt\/slides\/slide\d+\.xml$/.test(p)).sort((a,b)=>Number(a.match(/slide(\d+)/)[1])-Number(b.match(/slide(\d+)/)[1]));if(entries.length>20)throw Error('PPTX 最多导入 20 页');
 async function read(p,max=8e6){let f=zip.file(p);if(!f)return '';let content=await f.async('string');if(content.length>max)throw Error('PPTX XML 过大');return content;}
 let presentation=xml(await read('ppt/presentation.xml')),sz=first(presentation,'sldSz'),ow=attr(sz,'cx',9144000),oh=attr(sz,'cy',6858000),w=1600,h=Math.round(1600*oh/ow),factor=w/ow;
 for(const path of entries){let slide=xml(await read(path)),relPath=path.replace('/slides/','/slides/_rels/')+'.rels',relsText=await read(relPath),rels=new Map();if(relsText)nodes(xml(relsText),'Relationship').forEach(n=>{if(n.getAttribute('TargetMode')!=='External')rels.set(n.getAttribute('Id'),n.getAttribute('Target'));});let objects=[],skipped=0;
 for(const node of [...nodes(slide,'sp'),...nodes(slide,'pic')]){let xfrm=first(node,'xfrm');if(!xfrm){skipped++;continue;}let off=first(xfrm,'off'),ext=first(xfrm,'ext'),x=attr(off,'x')*factor,y=attr(off,'y')*factor,bw=attr(ext,'cx')*factor,bh=attr(ext,'cy')*factor;if(bw<1||bh<1)continue;let rotation=attr(xfrm,'rot')/60000;
 let tx=first(node,'txBody');if(tx){const paragraphs=nodes(tx,'p').map(p=>nodes(p,'t').map(t=>t.textContent).join(''));let p=first(tx,'rPr')||first(tx,'defRPr'),fill=first(p||node,'srgbClr'),fontSize=Math.max(10,Math.min(250,attr(p,'sz',2400)/100*1.6));objects.push(new F.Textbox(paragraphs.join('\n'),{left:x,top:y,width:bw,fontSize,fontFamily:'Microsoft YaHei, sans-serif',fill:fill?'#'+fill.getAttribute('val'):'#202020',fontWeight:p?.getAttribute('b')==='1'?'bold':'normal',angle:rotation,name:'PPTX 文字',role:fontSize>60?'title':'body'}).toObject());}
 else if(node.localName==='pic'){let blip=first(node,'blip'),id=blip?.getAttributeNS('http://schemas.openxmlformats.org/officeDocument/2006/relationships','embed'),target=rels.get(id);if(!target){skipped++;continue;}let parts=('ppt/slides/'+target).split('/'),resolved=[];for(const p of parts){if(p==='..')resolved.pop();else if(p!=='.')resolved.push(p);}let entry=zip.file(resolved.join('/'));if(!entry||!/\.(png|jpe?g|webp)$/i.test(target)){skipped++;continue;}let blob=await entry.async('blob');if(blob.size>25e6)throw Error('PPTX 图片过大');let type=/\.png$/i.test(target)?'png':/\.webp$/i.test(target)?'webp':'jpeg',base64=await entry.async('base64'),img=await F.FabricImage.fromURL('data:image/'+type+';base64,'+base64);img.set({left:x,top:y,scaleX:bw/img.width,scaleY:bh/img.height,angle:rotation,name:'PPTX 图片',role:'photo'});objects.push(img.toObject());}
 else{let fill=first(node,'srgbClr');if(fill)objects.push(new F.Rect({left:x,top:y,width:bw,height:bh,fill:'#'+fill.getAttribute('val'),angle:rotation,name:'PPTX 基础形状',role:'other'}).toObject());else skipped++;}}
 await E.addImportedPage({width:w,height:h,canvas:{background:'#ffffff',objects}});if(skipped)E.toast('此页有 '+skipped+' 项高级效果未导入；请与原版核对');}
 E.toast('PPTX 基础元素已导入；母版、复杂形状与特效需核对');
}
window.ZTH_IMPORT={pdf,pptx};
