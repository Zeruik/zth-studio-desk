'use strict';
const path=require('node:path'),{buildProduct}=require('./build-product.cjs');
buildProduct({modules:process.env.ZTH_BUILD_MODULES?path.resolve(process.env.ZTH_BUILD_MODULES):path.join(__dirname,'build-runtime/node_modules'),cacheDir:process.env.ZTH_RUNTIME_CACHE?path.resolve(process.env.ZTH_RUNTIME_CACHE):path.join(__dirname,'.cache')}).then(r=>console.log(JSON.stringify(r,null,2))).catch(e=>{console.error(e.message);process.exitCode=1});
