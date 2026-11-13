// Gera src/recortes.json: os pontos de cada recorte em halftone do portfólio
// (src/art.js, copiado de joaobyss.github.io/js/art.js). Roda uma vez:
//   node extrai_recortes.js
// Precisa de Playwright (Chromium) porque os desenhos usam canvas 2D.
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.setContent('<html><body></body></html>');
  await p.addScriptTag({ content: fs.readFileSync(__dirname + '/src/art.js', 'utf8') });
  const out = await p.evaluate(() => {
    const res = {};
    const ART = window.PF_ART.shapes;
    // capitular do "sobre": mesma receita do glyph() de art.js
    ART.capR = { cells: 34, dot: 'square', draw: (g, n) => {
      g.setTransform(1, 0, 0, 1, 0, 0);
      g.font = 'bold ' + (n * 1.0) + 'px Helvetica, Arial, sans-serif';
      g.textAlign = 'center'; g.textBaseline = 'middle';
      const l = g.createLinearGradient(0, 0, n, n); l.addColorStop(0, '#ffffff'); l.addColorStop(1, '#6a6a6a');
      g.fillStyle = l; g.fillText('R', n / 2, n * 0.56);
    } };
    for (const name of Object.keys(ART)) {
      const def = ART[name], n = def.cells;
      const src = document.createElement('canvas'); src.width = src.height = n;
      const g = src.getContext('2d', { willReadFrequently: true });
      g.scale(n, n); def.draw(g, n);
      const d = g.getImageData(0, 0, n, n).data, pts = [];
      for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) {
        const k = (j * n + i) * 4;
        const v = (d[k] * .299 + d[k + 1] * .587 + d[k + 2] * .114) / 255 * (d[k + 3] / 255);
        if (v >= 0.06) pts.push([i, j, Math.round(Math.sqrt(v) * 1000) / 1000]);
      }
      res[name] = { cells: n, dot: def.dot, pts };
    }
    return res;
  });
  fs.writeFileSync(__dirname + '/src/recortes.json', JSON.stringify(out));
  console.log(Object.entries(out).map(([k, v]) => k + ':' + v.pts.length).join(' '));
  await b.close();
})();
