'use strict';
const path=require('node:path'),{preparePython,prepareElectron}=require('./runtime-tools.cjs');
if(require.main===module)Promise.all([preparePython(path.resolve(process.env.ZTH_RUNTIME_CACHE||path.join(__dirname,'.cache'))),prepareElectron(path.resolve(process.env.ZTH_RUNTIME_CACHE||path.join(__dirname,'.cache')))]).then(r=>console.log(JSON.stringify(r,null,2))).catch(e=>{console.error(e.message);process.exitCode=1});
