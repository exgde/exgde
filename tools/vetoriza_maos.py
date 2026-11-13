"""Converte src/maos.png (mãos em pontos) numa lista de pontos [x, y, brilho].

Cada linha de pontos da imagem vira uma faixa; em cada faixa os picos do
perfil horizontal são os pontos. Saída: src/maos.json (coordenadas em px
da imagem original, brilho 0..1).
"""
import json
import numpy as np
from PIL import Image
from scipy.signal import find_peaks

a = np.array(Image.open('src/maos.png').convert('L')).astype(float) / 255
rows, _ = find_peaks(a.sum(1), height=a.sum(1).max() * 0.05, distance=5)
pts = []
for y in rows:
    band = a[y - 3:y + 4]
    prof = band.sum(0)
    xs, _ = find_peaks(prof, height=0.35, distance=3)
    for x in xs:
        cell = band[:, max(0, x - 2):x + 2]
        v = min(1.0, cell.sum() / 6.0)
        # centro vertical ponderado pelo brilho
        w = cell.sum(1)
        cy = y - 3 + (w * np.arange(len(w))).sum() / max(w.sum(), 1e-6)
        pts.append([int(x), round(float(cy), 1), round(v, 2)])
json.dump({'w': a.shape[1], 'h': a.shape[0], 'pts': pts}, open('src/maos.json', 'w'))
v = np.array([p[2] for p in pts])
print(len(pts), 'pontos; brilho min/med/max', v.min(), np.median(v), v.max())
