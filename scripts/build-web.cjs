const fs=require('node:fs');fs.rmSync('web',{recursive:true,force:true});fs.cpSync('app','web',{recursive:true});console.log('Offline web distribution prepared in web/');
