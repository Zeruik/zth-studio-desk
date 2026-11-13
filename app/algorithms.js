(function(root){
// RGB Euclidean distance normalized to a 0..255 tolerance; connected fixed-range flood fill.
function removeColor(data,width,height,seedX,seedY,tolerance=32,contiguous=true,softness=8){
 const out=new Uint8ClampedArray(data), sx=Math.max(0,Math.min(width-1,Math.round(seedX))),sy=Math.max(0,Math.min(height-1,Math.round(seedY))),p=(sy*width+sx)*4;
 const color=[data[p],data[p+1],data[p+2]],n=width*height,seen=new Uint8Array(n),queue=new Int32Array(n);let head=0,tail=0,count=0;
 const distance=i=>Math.hypot(data[i*4]-color[0],data[i*4+1]-color[1],data[i*4+2]-color[2])/Math.sqrt(3);
 function apply(i){let d=distance(i);if(d>tolerance+softness)return false;out[i*4+3]=Math.round(data[i*4+3]*(softness>0?Math.min(1,Math.max(0,(d-tolerance)/softness)):0));count++;return d<=tolerance;}
 if(contiguous){queue[tail++]=sy*width+sx;seen[sy*width+sx]=1;while(head<tail){let i=queue[head++];if(!apply(i))continue;const x=i%width,y=Math.floor(i/width);for(const j of [x>0?i-1:-1,x<width-1?i+1:-1,y>0?i-width:-1,y<height-1?i+width:-1])if(j>=0&&!seen[j]){seen[j]=1;queue[tail++]=j;}}}
 else for(let i=0;i<n;i++)apply(i);
 return {data:out,count,color};
}
function validateProject(doc){
 if(!doc||doc.format!=='zthpmsj'||doc.schema!==1)throw Error('不支持的工程格式或版本，请使用兼容版本打开。');
 if(!Array.isArray(doc.pages)||doc.pages.length<1||doc.pages.length>30)throw Error('工程需包含 1–30 页。');
 if(doc.fonts){if(!Array.isArray(doc.fonts)||doc.fonts.length>1||doc.fonts.some(f=>f.family!=='ZTH Sans'||typeof f.src!=='string'||!f.src.startsWith('data:font/woff2;base64,')||f.src.length>30000000))throw Error('内嵌字体无效');}
 const allowed=new Set(['rect','circle','ellipse','triangle','line','path','polygon','polyline','textbox','i-text','text','image','group','linear','radial']);
 let count=0;
 function walk(v){if(!v||typeof v!=='object')return; if(Array.isArray(v)){v.forEach(walk);return;}for(const [k,x]of Object.entries(v)){if(['__proto__','constructor','prototype'].includes(k))throw Error('工程含非法字段');if(['left','top','scaleX','scaleY','angle','fontSize','opacity','width','height'].includes(k)&&typeof x==='number'&&(!Number.isFinite(x)||Math.abs(x)>100000))throw Error('工程数值超限');if(k==='src'&&(typeof x!=='string'||!/^data:image\/(png|jpeg|webp);base64,/.test(x)))throw Error('工程图片必须内嵌为 PNG / JPG / WebP');if(k==='type'&&typeof x==='string'&&!allowed.has(x.toLowerCase()))throw Error('工程包含不支持的元素类型');if(k==='objects'&&Array.isArray(x)){count+=x.length;if(count>2500)throw Error('工程元素超过 2500 个');}walk(x);}}
 doc.pages.forEach(p=>{if(!Number.isFinite(p.width)||!Number.isFinite(p.height)||p.width<100||p.height<100||p.width>8000||p.height>8000||p.width*p.height>24000000)throw Error('画布尺寸超限（单页最多 2400 万像素）');walk(p.canvas);});return doc;
}
function autoLayout(items,w,h,variant=0){
 const m=w*.065,g=w*.025,roles={title:[],body:[],photo:[],logo:[],qr:[],other:[]};items.forEach(i=>(roles[i.role]||roles.other).push(i));const result=[];
 const add=(item,x,y,width,height)=>result.push({...item,x,y,width,height});
 const logoWidth=Math.min(w*.22,(w-2*m)/Math.max(1,roles.logo.length)-g);
 roles.logo.forEach((i,n)=>add(i,m+n*(logoWidth+g),h*.045,logoWidth,h*.085));
 const titleTop=h*.17,titleHeight=h*.15/Math.max(1,roles.title.length);
 roles.title.forEach((i,n)=>add(i,m,titleTop+n*titleHeight,w-2*m,titleHeight*.94));
 const top=h*.36,bottom=h*.79,area=bottom-top;
 const bodies=roles.body,photos=roles.photo;
 if(variant%3===1){photos.forEach((i,n)=>add(i,w*.53,top+n*area/Math.max(1,photos.length),w*.405,area/Math.max(1,photos.length)-g));bodies.forEach((i,n)=>add(i,m,top+n*area/Math.max(1,bodies.length),photos.length?w*.425:w*.87,area/Math.max(1,bodies.length)-g));}
 else{const cols=photos.length>2?3:Math.max(1,photos.length),rows=Math.ceil(photos.length/cols),photoArea=photos.length?(bodies.length?area*.52:area):0;
 photos.forEach((i,n)=>add(i,m+(n%cols)*(w-2*m+g)/cols,top+Math.floor(n/cols)*photoArea/Math.max(1,rows),(w-2*m-g*(cols-1))/cols,photoArea/Math.max(1,rows)-g));
 const bodyTop=top+photoArea,bodyArea=area-photoArea,bc=variant%3===2?1:(bodies.length>4?3:bodies.length>1?2:1),br=Math.ceil(bodies.length/bc);
 bodies.forEach((i,n)=>add(i,m+(n%bc)*(w-2*m+g)/bc,bodyTop+Math.floor(n/bc)*bodyArea/Math.max(1,br),(w-2*m-g*(bc-1))/bc,Math.max(10,bodyArea/Math.max(1,br)-g)));}
 const qrSize=Math.min(w*.16,(w-2*m)/Math.max(1,roles.qr.length)-g);roles.qr.forEach((i,n)=>add(i,w-m-qrSize-n*(qrSize+g),h-m-qrSize,qrSize,qrSize));
 // Decorative objects are intentionally untouched; this prevents grids and flourishes becoming content.
 return result;
}
root.ZTH_ALGORITHMS={removeColor,validateProject,autoLayout};if(typeof module!=='undefined')module.exports=root.ZTH_ALGORITHMS;
})(typeof window==='undefined'?globalThis:window);
