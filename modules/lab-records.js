/* Bounded, inert experiment snapshots; restored values never execute code. */
(function(root){'use strict';
const marker='ZTH_LAB_SNAPSHOT_V1:';
function validate(s){if(!s||typeof s!=='object'||Array.isArray(s))throw Error('INVALID_SNAPSHOT');const out={};for(const [k,min,max]of [['v',.5,24],['r1',100,100000],['r2',100,100000],['c',.000001,.001],['time',0,100000]]){if(typeof s[k]!=='number'||!Number.isFinite(s[k])||s[k]<min||s[k]>max)throw Error('INVALID_SNAPSHOT_'+k);out[k]=s[k];}if(s.load!==null&&(!Number.isFinite(s.load)||s.load<100||s.load>1000000))throw Error('INVALID_SNAPSHOT_load');out.load=s.load;if(!['','up','down','same'].includes(s.prediction)||typeof s.note!=='string'||s.note.length>4000)throw Error('INVALID_SNAPSHOT_NOTE');out.prediction=s.prediction;out.note=s.note;return out;}
function encode(s){return marker+JSON.stringify(validate(s));}
function decode(body){if(typeof body!=='string'||body.length>64000)return null;const line=body.split('\n').findLast(x=>x.startsWith(marker));if(!line)return null;try{return validate(JSON.parse(line.slice(marker.length)));}catch{return null;}}
const api={validate,encode,decode};root.DeskLabRecords=api;if(typeof module==='object')module.exports=api;
})(typeof window==='undefined'?globalThis:window);
