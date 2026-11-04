// Print an SVG to a PDF page of the given physical width (mm); height follows the viewBox.
const { chromium } = require('playwright');
const fs = require('fs'); const path = require('path');
(async () => {
  const [,, inFile, outFile, widthMmArg] = process.argv;
  const widthMm = parseFloat(widthMmArg || '183');
  const svg = fs.readFileSync(inFile, 'utf8');
  const m = svg.match(/viewBox="([\d.\s-]+)"/);
  const [, , w, h] = m[1].trim().split(/\s+/).map(Number);
  const heightMm = widthMm * h / w;
  const html = `<!doctype html><html><head><meta charset="utf-8"><style>
    @page { size: ${widthMm}mm ${heightMm}mm; margin: 0; }
    html, body { margin: 0; padding: 0; background: #fff; }
    svg { display: block; width: ${widthMm}mm; height: ${heightMm}mm; }
  </style></head><body>${svg.replace(/<svg /, '<svg style="width:' + widthMm + 'mm;height:' + heightMm + 'mm" ')}</body></html>`;
  const tmp = path.resolve(outFile + '.html'); fs.writeFileSync(tmp, html);
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + tmp); await page.waitForTimeout(300);
  await page.pdf({ path: outFile, width: `${widthMm}mm`, height: `${heightMm}mm`, printBackground: true, preferCSSPageSize: true });
  await browser.close();
  console.log('wrote', outFile, `${widthMm} x ${heightMm.toFixed(1)} mm`);
})();
