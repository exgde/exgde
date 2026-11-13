/* ============================================================
   RECORTES — arte em halftone gerada no navegador.

   Cada <canvas data-art="nome"> recebe um desenho: a forma é pintada
   em tons de cinza numa grade minúscula (uma célula = um ponto) e cada
   célula vira um ponto branco cujo tamanho segue o brilho.

   De cada forma também sai um contorno (canvas._contour, pontos 0..1),
   que o overlay de tracking usa para "seguir" o recorte.

   Para criar um recorte novo: adicione uma entrada em ART e use o nome
   em data-art no index.html.
   ============================================================ */
(function () {
  'use strict';

  var TAU = Math.PI * 2;

  function lin(g, x0, y0, x1, y1, a, b) {
    var l = g.createLinearGradient(x0, y0, x1, y1);
    l.addColorStop(0, a); l.addColorStop(1, b);
    return l;
  }
  function rad(g, x, y, r, a, b) {
    var l = g.createRadialGradient(x, y, 0, x, y, r);
    l.addColorStop(0, a); l.addColorStop(1, b);
    return l;
  }
  function starPath(g, R, r, n, rot) {
    g.beginPath();
    for (var i = 0; i < n * 2; i++) {
      var a = rot + i * Math.PI / n, q = i % 2 ? r : R;
      g[i ? 'lineTo' : 'moveTo'](0.5 + Math.cos(a) * q, 0.5 + Math.sin(a) * q);
    }
    g.closePath();
  }
  function about(g, angle, scale) {            // gira/escala em torno do centro
    g.translate(0.5, 0.5); g.rotate(angle); g.scale(scale, scale); g.translate(-0.5, -0.5);
  }
  function glyph(g, n, ch, size, dy) {         // letra grande, em pixels da grade
    g.setTransform(1, 0, 0, 1, 0, 0);
    g.font = 'bold ' + (n * size) + 'px Helvetica, Arial, sans-serif';
    g.textAlign = 'center'; g.textBaseline = 'middle';
    g.fillStyle = lin(g, 0, 0, n, n, '#ffffff', '#6a6a6a');
    g.fillText(ch, n / 2, n * (0.5 + dy));
  }

  /* cells = pontos por lado; dot = 'round' | 'square'. As formas são
     desenhadas num quadrado 0..1. */
  var ART = {
    star: { cells: 56, dot: 'round', draw: function (g) {
      starPath(g, 0.5, 0.12, 4, -0.35);  g.fillStyle = rad(g, 0.5, 0.5, 0.5, '#ffffff', '#7c7c7c'); g.fill();
      starPath(g, 0.31, 0.08, 4, -0.35); g.fillStyle = '#000'; g.fill();
      starPath(g, 0.18, 0.05, 4, -0.35); g.fillStyle = '#fff'; g.fill();
    } },

    floppy: { cells: 46, dot: 'round', draw: function (g) {
      about(g, -0.2, 0.92);
      g.beginPath();
      g.moveTo(0.14, 0.12); g.lineTo(0.76, 0.12); g.lineTo(0.88, 0.24);
      g.lineTo(0.88, 0.88); g.lineTo(0.14, 0.88); g.closePath();
      g.fillStyle = lin(g, 0.14, 0.12, 0.88, 0.88, '#cfcfcf', '#555555'); g.fill();
      g.fillStyle = '#1a1a1a'; g.fillRect(0.3, 0.12, 0.36, 0.25);       // tampa metálica
      g.fillStyle = '#f0f0f0'; g.fillRect(0.52, 0.15, 0.09, 0.19);      // janela da tampa
      g.fillStyle = '#ffffff'; g.fillRect(0.24, 0.5, 0.54, 0.38);       // etiqueta
      g.fillStyle = '#4a4a4a';
      [0.58, 0.67, 0.76].forEach(function (y) { g.fillRect(0.3, y, 0.42, 0.03); });
    } },

    chip: { cells: 54, dot: 'square', draw: function (g) {
      about(g, 0.5, 0.78);
      g.fillStyle = '#9a9a9a';
      for (var i = 0; i < 7; i++) {
        var p = 0.245 + i * 0.08;
        g.fillRect(p, 0.08, 0.035, 0.14); g.fillRect(p, 0.78, 0.035, 0.14);
        g.fillRect(0.08, p, 0.14, 0.035); g.fillRect(0.78, p, 0.14, 0.035);
      }
      g.fillStyle = lin(g, 0.2, 0.2, 0.8, 0.8, '#ececec', '#585858'); g.fillRect(0.2, 0.2, 0.6, 0.6);
      g.fillStyle = '#141414'; g.fillRect(0.32, 0.32, 0.36, 0.36);
      g.fillStyle = rad(g, 0.5, 0.5, 0.17, '#ffffff', '#141414');
      g.beginPath(); g.arc(0.5, 0.5, 0.17, 0, TAU); g.fill();
    } },

    burst: { cells: 72, dot: 'square', px: 900, draw: function (g) {
      for (var k = 0; k < 5; k++) {
        g.save();
        g.translate(0.5, 0.5); g.rotate(k * TAU / 5 - 0.3);
        g.beginPath(); g.ellipse(0, -0.27, 0.14, 0.23, 0, 0, TAU);
        g.fillStyle = rad(g, 0, -0.2, 0.3, '#a8a8a8', '#2c2c2c'); g.fill();
        g.restore();
      }
      g.fillStyle = rad(g, 0.5, 0.5, 0.22, '#ffffff', 'rgba(255,255,255,0)');
      g.beginPath(); g.arc(0.5, 0.5, 0.22, 0, TAU); g.fill();
    } },

    cursor: { cells: 38, dot: 'round', draw: function (g) {
      var pts = [[0.22, 0.08], [0.22, 0.84], [0.41, 0.66], [0.55, 0.94], [0.68, 0.88], [0.54, 0.6], [0.8, 0.6]];
      g.beginPath();
      pts.forEach(function (p, i) { g[i ? 'lineTo' : 'moveTo'](p[0], p[1]); });
      g.closePath();
      g.fillStyle = lin(g, 0.22, 0.08, 0.7, 0.9, '#ffffff', '#707070'); g.fill();
    } },

    at:     { cells: 44, dot: 'round', draw: function (g, n) { glyph(g, n, '@', 0.92, 0.02); } },
    braces: { cells: 44, dot: 'round', draw: function (g, n) { glyph(g, n, '{}', 0.8, 0); } }
  };

  function lum(d, n, i, j) {
    var k = (j * n + i) * 4;
    return (d[k] * 0.299 + d[k + 1] * 0.587 + d[k + 2] * 0.114) / 255 * (d[k + 3] / 255);
  }

  /* contorno: de 18 direções, anda de fora para dentro até achar tinta */
  function contour(d, n) {
    var pts = [], A = 18;
    for (var a = 0; a < A; a++) {
      var th = a / A * TAU, cx = Math.cos(th), cy = Math.sin(th);
      for (var r = 0.72; r > 0.04; r -= 0.5 / n) {
        var x = 0.5 + cx * r, y = 0.5 + cy * r;
        if (x < 0 || y < 0 || x >= 1 || y >= 1) continue;
        if (lum(d, n, Math.floor(x * n), Math.floor(y * n)) > 0.14) { pts.push([x, y]); break; }
      }
    }
    return pts.length > 4 ? pts : null;
  }

  function render(canvas) {
    var def = ART[canvas.getAttribute('data-art')];
    if (!def) return;
    var n = def.cells;

    var src = document.createElement('canvas');
    src.width = src.height = n;
    var g = src.getContext('2d', { willReadFrequently: true });
    g.scale(n, n);
    def.draw(g, n);
    var d = g.getImageData(0, 0, n, n).data;

    var out = def.px || 640, step = out / n;
    canvas.width = canvas.height = out;
    var c = canvas.getContext('2d');
    c.clearRect(0, 0, out, out);
    c.fillStyle = '#fff';
    for (var j = 0; j < n; j++) {
      for (var i = 0; i < n; i++) {
        var v = lum(d, n, i, j);
        if (v < 0.06) continue;
        var x = (i + 0.5) * step, y = (j + 0.5) * step, s = Math.sqrt(v);
        if (def.dot === 'square') {
          var w = step * s * 0.94;
          c.fillRect(x - w / 2, y - w / 2, w, w);
        } else {
          c.beginPath(); c.arc(x, y, step * 0.56 * s, 0, TAU); c.fill();
        }
      }
    }
    canvas._contour = contour(d, n);
  }

  function renderAll() {
    [].forEach.call(document.querySelectorAll('canvas[data-art]'), render);
  }

  window.PF_ART = { render: render, renderAll: renderAll, shapes: ART };
  renderAll();
})();
