const {chromium,webkit,devices}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const http=require('node:http');
const pageFile='onyx-2025-v3.html';
const source=fs.readFileSync(pageFile,'utf8');
const publicUrl='https://damienreilley.github.io/reilleyrips/'+pageFile;
async function run(browserType,device,url){
 const browser=await browserType.launch({headless:true});
 try{
  const context=await browser.newContext(device);
  const page=await context.newPage();
  const errors=[];page.on('pageerror',e=>errors.push(String(e)));
  const response=await page.goto(url,{waitUntil:'load',timeout:30000});
  assert.equal(response.status(),200);
  assert.equal(await page.locator('h1').textContent(),'2025 Onyx Vintage Extended');
  assert.equal(await page.locator('#player option').count(),56);
  assert.equal(await page.locator('#search').count(),0);
  assert.equal(await page.locator('#card-details').isVisible(),false);
  await page.selectOption('#player','Colt Emerson');
  assert.equal(await page.locator('#card-details').isVisible(),true);
  await page.click('#identify');
  assert.match(await page.locator('#result').innerText(),/Colt Emerson/);
  assert.match(await page.locator('#result').innerText(),/Unsigned base/);
  await page.click('#reset');
  assert.equal(await page.locator('#result').isVisible(),false);
  await page.selectOption('#player','Kevin McGonigle');
  await page.selectOption('#kind','auto');
  await page.selectOption('#color','Blue');
  await page.fill('#serial','07/35');
  await page.selectOption('#inscription',{index:1});
  await page.click('#identify');
  let result=await page.locator('#result').innerText();
  assert.match(result,/Kevin McGonigle/);assert.match(result,/advertised \/35/);
  assert.match(result,/inscription/);assert.match(result,/07\/35/);
  const search=await page.locator('#result a').getAttribute('href');
  assert.match(decodeURIComponent(search),/Kevin McGonigle/);
  await page.getByRole('button',{name:'Copy card description'}).click();
  assert.match(await page.locator('#result button').innerText(),/Copied|Copy unavailable/);
  await page.fill('#serial','99/10');
  await page.click('#identify');
  assert.match(await page.locator('#result').innerText(),/Check the serial number format/);
  assert.match(await page.locator('#result').innerText(),/denominator differs/);
  await page.click('#reset');
  await page.selectOption('#player','Colt Emerson');
  await page.selectOption('#kind','auto');
  await page.click('#identify');
  assert.match(await page.locator('#result').innerText(),/not on checklist/);
  await page.getByText('Autograph color guide',{exact:true}).click();
  assert.equal(await page.locator('#guide tr').count(),11);
  await page.getByText('Full checklist',{exact:true}).click();
  assert.equal(await page.locator('#list tr').count(),55);
  await page.fill('#filter','Kruz Schoolcraft');
  assert.equal(await page.locator('#list tr').count(),1);
  assert.match(await page.locator('#list').innerText(),/Kruz Schoolcraft/);
  await page.fill('#filter','not-a-player');
  assert.match(await page.locator('#list').innerText(),/No matches/);
  await page.getByText('Sources and set facts',{exact:true}).click();
  assert.equal(await page.locator('details a').count(),3);
  if(url.includes('github.io')) { await page.locator('a[href="#guide"]').click(); assert.equal(await page.locator('#guide').isVisible(),true); assert.equal(new URL(page.url()).hash,'#guide'); }
  for(const a of await page.locator('details a[href^="https:"]').all()){const href=await a.getAttribute('href');const response=await context.request.get(href,{timeout:20000});assert.ok(response.ok(),href+' HTTP '+response.status());console.log('PASS reference',response.status(),href);}
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
  assert.deepEqual(errors,[]);
  console.log('PASS',browserType.name(),device.viewport,url);
 }finally{await browser.close()}
}
(async()=>{
 const server=http.createServer((req,res)=>{res.setHeader('Content-Type','text/html; charset=utf-8');res.end(source)});
 await new Promise(r=>server.listen(0,'127.0.0.1',r));
 try{
  const local='http://127.0.0.1:'+server.address().port+'/';
  // Public browser tests below verify the deployed revision.
  let response;
  for(let i=0;i<8;i++){
   try{response=await fetch(publicUrl+'?verification=4',{signal:AbortSignal.timeout(15000)});if(response.ok&&(await response.text()).includes('Distributor parallel specifications (in this guide)'))break;}catch{}
   await new Promise(r=>setTimeout(r,5000));
  }
  await run(webkit,devices['iPhone 13'],publicUrl+'?verification=4');
  await run(chromium,{viewport:{width:1280,height:800}},publicUrl+'?verification=4');
 }finally{server.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
