const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1920,height:1080}});
await p.goto('file:///home/user/Hasiraamv/motion/capabilities.html');await p.addStyleTag({content:'#hint{display:none}'});await p.waitForTimeout(300);
for(let f=0;f<1200;f++){await p.evaluate(ms=>window.__render(ms),f*1000/60);
 await p.screenshot({path:`/tmp/fr/${String(f).padStart(5,'0')}.jpg`,type:'jpeg',quality:92});}
await b.close()})();
