// Rasterise an SVG file (the user's own figure) with Chromium at a given scale.
const { chromium } = require('playwright');
const fs = require('fs'); const path = require('path');
(async () => {
  const [,, inFile, outFile, scaleArg] = process.argv;
  const scale = parseFloat(scaleArg || '3');
  const svg = fs.readFileSync(inFile, 'utf8');
  const m = svg.match(/viewBox="([\d.\s-]+)"/);
  const [, , w, h] = m ? m[1].trim().split(/\s+/).map(Number) : [0,0,800,600];
  const html = `<!doctype html><html><head><meta charset="utf-8"><style>html,body{margin:0;background:#fff}svg{display:block}</style></head><body>${svg.replace(/<svg /, `<svg style="width:${w}px;height:${h}px" `)}</body></html>`;
  const tmp = path.resolve(outFile + '.html');
  fs.writeFileSync(tmp, html);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: Math.ceil(w), height: Math.ceil(h) }, deviceScaleFactor: scale });
  await page.goto('file://' + tmp);
  await page.waitForTimeout(300);
  await page.screenshot({ path: outFile, fullPage: true });
  await browser.close();
  console.log('wrote', outFile, w, 'x', h, 'at', scale);
})();
