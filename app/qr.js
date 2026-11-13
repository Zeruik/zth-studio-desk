import QRCode from './vendor/qrcode.mjs';
window.makeQR=(text,colors={})=>QRCode.toDataURL(text,{width:700,margin:3,errorCorrectionLevel:'M',color:{dark:(colors.dark||'#142c4a')+'ff',light:(colors.light||'#ffffff')+'ff'}});
