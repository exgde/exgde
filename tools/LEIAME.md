# tools

Gera as imagens de `assets/` usadas no README do perfil.

```
python3 tools/gera.py
```

- Todo o texto (bio, ficha, stack, projetos, links) fica em `CONTEUDO`, no topo de `gera.py`.
- Precisa de `fonttools`, `brotli` e `Pillow` (`pip install fonttools brotli pillow`).
- `src/recortes.json` sai de `node tools/extrai_recortes.js`, que lê os recortes em halftone de `src/art.js` (cópia de `exgde.github.io/js/art.js`). Só precisa rodar de novo se mudar um recorte.
- `src/maos.json` sai de `python3 tools/vetoriza_maos.py`, que converte `src/maos.png` em pontos vetoriais.

## Créditos

- Fontes [VT323](https://fonts.google.com/specimen/VT323) e [Inter](https://rsms.me/inter/), licença OFL. Vão embutidas nos SVGs, só com os caracteres usados.
- Ícones da stack: [Simple Icons](https://simpleicons.org/) (CC0). As marcas pertencem aos donos.
- Captura da Casa Acessível: do portfólio.
