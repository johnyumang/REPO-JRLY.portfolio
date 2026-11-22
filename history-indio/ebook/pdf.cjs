// html -> 6x9 in PDF with the Playwright Chromium that is pre-installed on the build machine.
const { chromium } = require('playwright');
const { pathToFileURL } = require('url');
const [, , html, pdf] = process.argv;
(async () => {
const b = await chromium.launch(); const p = await b.newPage();
await p.goto(pathToFileURL(html).href, { waitUntil: 'load' });
await p.pdf({ path: pdf, width: '6in', height: '9in', printBackground: true, preferCSSPageSize: true,
  displayHeaderFooter: true, headerTemplate: '<span></span>',
  footerTemplate: '<div style="width:100%;text-align:center;font-size:8px;color:#555"><span class="pageNumber"></span></div>' });
await b.close();
})();
