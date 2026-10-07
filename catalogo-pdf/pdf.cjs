// Convierte catalogo.html en el PDF final (A4, alta calidad) con Chromium.
const path = require('path');
const { chromium } = require(process.env.PLAYWRIGHT_PATH || 'playwright');
(async () => {
  const salida = process.argv[2] || path.join(__dirname, '..', 'Catalogo-OBREGOM.pdf');
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto('file://' + path.join(__dirname, 'catalogo.html'), { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  await p.pdf({ path: salida, format: 'A4', printBackground: true, preferCSSPageSize: true });
  await b.close();
  console.log('PDF listo:', salida);
})();
