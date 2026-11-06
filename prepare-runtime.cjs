'use strict';
const path=require('node:path'),{preparePython}=require('./runtime-tools.cjs');
if(require.main===module)preparePython(path.resolve(process.env.ZTH_RUNTIME_CACHE||path.join(__dirname,'.cache'))).then(r=>console.log(JSON.stringify(r,null,2))).catch(e=>{console.error(e.message);process.exitCode=1});
