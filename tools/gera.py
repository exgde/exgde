"""Gera todas as imagens do README do perfil (assets/*.svg).

Mesma estética do portfólio (exgde.github.io): preto e branco, recortes em
halftone, cantoneiras de "tracking", VT323 no HUD e itálico nos títulos. Cada
peça sai em -dark e -light, porque o botão "inverter" do site aqui vira o tema
do GitHub. Os cartões dos repositórios imitam a tela do PSP e são pretos nos
dois temas, então têm uma versão só.

    python3 tools/gera.py          (a partir da raiz do repositório)

Todo o texto fica em CONTEUDO, logo abaixo. Dependências: fonttools e
brotli.
"""
import base64
import io
import json
import math
import os
import re
from xml.sax.saxutils import escape

from fontTools.subset import Options, Subsetter
from fontTools.ttLib import TTFont

AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(AQUI, '..', 'assets')
W = 840

# ------------------------------------------------------------------ conteúdo
CONTEUDO = {
    'tag': '#JOAOBYSS',
    'nome': 'joaobyss',
    'funcao': 'IA LOCAL  /  AUTOMAÇÃO  /  JOGOS',
    'status': 'PROCURANDO VAGA JR',
    'terminal': 'ligo IA local a ferramentas e rotinas. no tempo livre, faço jogos',
    'botoes': [  # (arquivo, rótulo, destaque)
        ('portfolio', 'PORTFÓLIO', True),
        ('linkedin', 'LINKEDIN', False),
        ('email', 'E-MAIL', False),
        ('itch', 'ITCH.IO', False),
    ],
    'secoes': [  # (arquivo, número, título, rótulo da direita)
        ('sobre', '01', 'SOBRE', 'PLAYER.INFO'),
        ('stack', '02', 'STACK', 'INVENTORY'),
        ('abertos', '03', 'CÓDIGO ABERTO', 'UMD.LIST'),
        ('andamento', '04', 'EM ANDAMENTO', 'SAVE.DATA'),
        ('contato', '05', 'CONTATO', 'LINK.CABLE'),
    ],
    'bio': ('Rodo modelos de linguagem no meu próprio computador desde 2023. Hoje '
            'trabalho mais com automação: faço o modelo mexer em ferramentas e dados de '
            'verdade, inclusive via MCP. Antes da IA vieram os jogos, e eles continuam. '
            'Agora estou no WW1-Thriller, um terror em terceira pessoa na Unreal Engine 5.'),
    'ficha': [
        ('QUERO', 'Vaga júnior em AI engineering ou automação'),
        ('FOCO', 'IA local, MCP, agentes e integração'),
        ('BASE', 'Ciência da Computação na UFJ'),
        ('SIDE QUEST', 'Jogos e mods desde 2019, na Unity e na Unreal'),
        ('COMBUSTÍVEL', 'Café, silêncio e uma GPU'),
    ],
    'icones': ['claude', 'python', 'typescript', 'nodedotjs', 'docker', 'sqlite', 'mysql',
               'git', 'swift', 'dotnet', 'unity', 'unrealengine', 'blender'],
    'tags': [
        ('IA E DADOS', ['LLMs locais', 'MCP', 'Claude Code', 'Contexto e parâmetros', 'SQLite', 'MySQL']),
        ('AUTOMAÇÃO', ['Node.js', 'TypeScript', 'Python', 'Docker', 'Playwright', 'Remotion', 'Git']),
        ('JOGOS E 3D', ['Unreal Engine 5', 'Blueprint', 'Unity', 'Blender', 'C#', 'Swift']),
    ],
    # repositórios públicos: (arquivo, caminho, título, descrição, stack, nota)
    'abertos': [
        ('portfolio', 'exgde/exgde.github.io', 'Portfólio',
         'Uma página só, com um PSP 3D que mostra os projetos. HTML, CSS e JS, sem build.',
         'THREE.JS · JAVASCRIPT', ''),
        ('adega', 'exgde/adega', 'Adega',
         'Meu CrossOver caseiro: um app de macOS que roda programas do Windows com Wine.',
         'SWIFT · SWIFTUI · WINE', ''),
        ('biblioteca-sql', 'exgde/biblioteca-sql', 'Biblioteca SQL',
         'Trabalho de Banco de Dados da UFJ. O modelo MySQL de uma biblioteca, com 12 consultas.',
         'MYSQL · MODELAGEM', ''),
        ('goldspotting', 'joaobyss.itch.io', 'Goldspotting',
         'Meu primeiro jogo lançado. Fiz na Unity e publiquei no itch.io.',
         'UNITY · ITCH.IO', ''),
        ('button-prompts', 'exgde/oot-switch2-button-prompts', 'Button Prompts',
         'Troca os ícones de botão do OOT (Switch 2) pelos de PlayStation, Xbox e Steam Deck.',
         'MOD · ROMFS · LAYEREDFS', '★ 45+'),
        ('teclado-mouse', 'exgde/oot-lichii-keyboard-mouse', 'Teclado + Mouse',
         'Pra jogar OOT no Lichii de teclado e mouse. Troca até os ícones e a tela de controles.',
         'PYTHON · POWERSHELL', ''),
    ],
    # privados, em lista: (título, descrição, estado)
    'andamento': [
        ('CUTSCENE-LOADER', 'Animação 3D a partir de vídeo comum, sem mocap. Exporta BVH pro Blender.', 'PRÉ-ALPHA'),
        ('Painel com MCP', 'Servidor MCP que mostra ao Claude o estado real das coisas. Um Qwen local dá o segundo parecer.', 'PREPARANDO'),
        ('Fábrica de vídeos', 'Roteiro, voz local e animação 3D feita em código. Nada vai ao ar sem eu aprovar.', 'PREPARANDO'),
        ('Prospecção', 'Busca, página de demonstração e fila de mensagens, com teto de custo. Eu aprovo cada envio.', 'PREPARANDO'),
        ('Casa Acessível', 'Experiência em VR para exposição num shopping da minha cidade: casa e banheiro adaptados a cadeirantes.', 'VR'),
        ('WW1-Thriller', 'Terror em terceira pessoa na Unreal Engine 5.8, todo em Blueprint.', 'EM PRODUÇÃO'),
    ],
    'andamento_nota': 'código fechado por enquanto. os de IA abrem quando eu terminar de tirar chaves e dados pessoais.',
    'contato': ['fale', 'comigo.'],
    'contato_txt': 'tô atrás de vaga júnior em AI engineering ou automação. freela e parceria também me interessam.',
    'rodape': ['joaobyss', 'feito com café  ·  exgde.github.io'],
}

# ------------------------------------------------------------------- temas
TEMAS = {
    'dark': dict(bg='#000000', fg='#ffffff', mute='#8a8a8a', line='#2e2e2e', trk='#808080'),
    'light': dict(bg='#ffffff', fg='#000000', mute='#6f6f6f', line='#d6d6d6', trk='#808080'),
}

# ------------------------------------------------------------------- fontes
FONTES = {  # família no CSS -> arquivo
    'M': 'vt323-latin-400-normal.woff2',      # HUD, mono pixelada
    'I': 'inter-latin-400-italic.woff2',      # títulos em itálico
    'R': 'inter-latin-400-normal.woff2',      # texto corrido
}
_tt = {k: TTFont(os.path.join(AQUI, 'fonts', v)) for k, v in FONTES.items()}


def medir(txt, fam, tam, esp=0.0):
    """Largura em px de um texto numa das fontes embutidas."""
    f = _tt[fam]
    cmap, hmtx, upm = f.getBestCmap(), f['hmtx'], f['head'].unitsPerEm
    w = 0
    for ch in txt:
        g = cmap.get(ord(ch)) or cmap.get(ord('?'))
        w += hmtx[g][0] / upm * tam + esp
    return w


def _subset(fam, chars):
    f = TTFont(os.path.join(AQUI, 'fonts', FONTES[fam]))
    op = Options()
    op.flavor = 'woff2'
    op.layout_features = ['kern', 'liga']
    s = Subsetter(op)
    s.populate(text=''.join(sorted(set(chars))) + ' ')
    s.subset(f)
    b = io.BytesIO()
    f.flavor = 'woff2'
    f.save(b)
    return base64.b64encode(b.getvalue()).decode()


def montar(nome, w, h, corpo, titulo, css='', fundo=None):
    """Fecha o SVG: embute só os glifos usados de cada fonte e grava."""
    usadas = {}
    for fam, txt in re.findall(r'class="[^"]*\bf([MIR])\b[^"]*"[^>]*>([^<]*)<', corpo):
        usadas.setdefault(fam, []).append(txt)
    for fam, txt in re.findall(r'class="[^"]*\bf([MIR])\b[^"]*"[^>]*>\s*<tspan[^>]*>([^<]*)<', corpo):
        usadas.setdefault(fam, []).append(txt)
    faces = []
    for fam, partes in usadas.items():
        chars = ''.join(partes)
        chars = chars.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        faces.append("@font-face{font-family:'%s';src:url(data:font/woff2;base64,%s) format('woff2')}"
                     % (fam, _subset(fam, chars)))
    estilo = (''.join(faces) +
              ".fM{font-family:'M',ui-monospace,monospace}"
              ".fI{font-family:'I','Helvetica Neue',Helvetica,Arial,sans-serif;font-style:italic}"
              ".fR{font-family:'R','Helvetica Neue',Helvetica,Arial,sans-serif}"
              "@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}"
              ".blink{animation:blink 1.1s steps(1) infinite}"
              "@keyframes cyc{0%,24.9%{opacity:1}25%,100%{opacity:0}}"
              + css +
              "@media (prefers-reduced-motion:reduce){*{animation:none!important}}")
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
           f'width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(titulo)}">'
           f'<title>{escape(titulo)}</title><style>{estilo}</style>'
           + (f'<rect width="{w}" height="{h}" fill="{fundo}"/>' if fundo else '')
           + corpo + '</svg>')
    with open(os.path.join(SAIDA, nome + '.svg'), 'w', encoding='utf-8') as fp:
        fp.write(svg)
    return len(svg)


def T(x, y, txt, fam, tam, cor, esp=0, anchor='start', extra='', cls=''):
    return (f'<text x="{x:.1f}" y="{y:.1f}" class="f{fam} {cls}" font-size="{tam}" fill="{cor}"'
            + (f' letter-spacing="{esp}"' if esp else '')
            + (f' text-anchor="{anchor}"' if anchor != 'start' else '')
            + f' {extra}>{escape(txt)}</text>')


def quebrar(txt, fam, tam, larguras):
    """Quebra em linhas; larguras[i] é a largura máxima da linha i (a última se repete)."""
    linhas, atual = [], ''
    for p in txt.split():
        teste = (atual + ' ' + p).strip()
        lim = larguras[min(len(linhas), len(larguras) - 1)]
        if medir(teste, fam, tam) <= lim or not atual:
            atual = teste
        else:
            linhas.append(atual)
            atual = p
    if atual:
        linhas.append(atual)
    return linhas


# --------------------------------------------------------- peças visuais
RECORTES = json.load(open(os.path.join(AQUI, 'src', 'recortes.json')))


def halftone(nome, x, y, tam, cor, opac=1.0):
    """Um recorte de art.js como pontos vetoriais num quadrado tam×tam."""
    d = RECORTES[nome]
    n, passo = d['cells'], tam / d['cells']
    out = [f'<g fill="{cor}"' + (f' opacity="{opac}"' if opac < 1 else '') + '>']
    for i, j, s in d['pts']:
        cx, cy = x + (i + .5) * passo, y + (j + .5) * passo
        if d['dot'] == 'square':
            w = passo * s * .94
            out.append(f'<rect x="{cx - w / 2:.1f}" y="{cy - w / 2:.1f}" width="{w:.1f}" height="{w:.1f}"/>')
        else:
            out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{passo * .56 * s:.2f}"/>')
    out.append('</g>')
    return ''.join(out)


def cantos(x, y, w, h, L, cor, sw=1):
    """Cantoneiras do tracking."""
    p = (f'M{x},{y + L}V{y}H{x + L}M{x + w - L},{y}H{x + w}V{y + L}'
         f'M{x + w},{y + h - L}V{y + h}H{x + w - L}M{x + L},{y + h}H{x}V{y + h - L}')
    return f'<path d="{p}" fill="none" stroke="{cor}" stroke-width="{sw}"/>'


def borda(w, h, t):
    return f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" fill="none" stroke="{t["line"]}"/>'


# ================================================================ peças
def banner(tema):
    t = TEMAS[tema]
    m = json.load(open(os.path.join(AQUI, 'src', 'maos.json')))
    H = 360
    y0, ox, oy = 270, (W - m['w']) / 2, 44   # recorte vertical da imagem original
    pts = [(x + ox, y - y0 + oy, v) for x, y, v in m['pts']]
    esq = [p for p in pts if p[0] < W / 2]
    dirt = [p for p in pts if p[0] >= W / 2]
    dots = [f'<g fill="{t["fg"]}">']
    for x, y, v in pts:
        dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{1.05 + .55 * math.sqrt(v):.2f}"/>')
    dots.append('</g>')

    def bbox(ps, pad=8):
        xs, ys = [p[0] for p in ps], [p[1] for p in ps]
        return min(xs) - pad, min(ys) - pad, max(xs) - min(xs) + 2 * pad, max(ys) - min(ys) + 2 * pad
    ponta_e = max(esq, key=lambda p: p[0])
    ponta_d = min(dirt, key=lambda p: p[0])
    c = [borda(W, H, t)]
    c.append(T(22, 28, CONTEUDO['tag'], 'M', 15, t['mute'], esp=1.5))
    sw = medir(CONTEUDO['status'], 'M', 15, 1.2)
    c.append(f'<circle cx="{W - 22 - sw - 12:.1f}" cy="23.5" r="3.5" fill="{t["fg"]}" class="pulse"/>')
    c.append(T(W - 22, 28, CONTEUDO['status'], 'M', 15, t['mute'], esp=1.2, anchor='end'))
    c.append(''.join(dots))
    for i, ps in enumerate((esq, dirt)):
        bx, by, bw, bh = bbox(ps)
        c.append(cantos(bx, by, bw, bh, 10, t['trk']))
        c.append(T(bx, by - 6, 'TRK_0%d' % (i + 1), 'M', 12, t['trk']))
    # a faísca entre os dedos
    ex, ey, dx_, dy_ = ponta_e[0] + 5, ponta_e[1], ponta_d[0] - 5, ponta_d[1]
    mx, my = (ex + dx_) / 2, (ey + dy_) / 2
    c.append(f'<line x1="{ex:.1f}" y1="{ey:.1f}" x2="{dx_:.1f}" y2="{dy_:.1f}" stroke="{t["trk"]}" stroke-dasharray="2 3"/>')
    c.append(f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="2.5" fill="{t["fg"]}"/>')
    c.append(f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="8" fill="none" stroke="{t["fg"]}" class="ring"/>')
    c.append(T(W / 2, 306, CONTEUDO['nome'], 'I', 72, t['fg'], esp=-1.5, anchor='middle'))
    c.append(T(W / 2, 336, CONTEUDO['funcao'], 'M', 17, t['mute'], esp=3, anchor='middle'))
    css = ('@keyframes pulse{0%,100%{opacity:1}50%{opacity:.2}}.pulse{animation:pulse 1.8s ease-in-out infinite}'
           '@keyframes ring{0%{transform:scale(.4);opacity:.8}100%{transform:scale(2);opacity:0}}'
           f'.ring{{transform-origin:{mx:.1f}px {my:.1f}px;animation:ring 2.8s ease-out infinite}}')
    return montar('banner-' + tema, W, H, ''.join(c),
                  'joaobyss: IA local, automação e jogos. Duas mãos desenhadas em pontos, quase se tocando.', css, t['bg'])


def terminal(tema):
    t = TEMAS[tema]
    H = 46
    txt = CONTEUDO['terminal']
    wtxt = medir('>_ ' + txt, 'M', 20, .5)
    x0 = (W - wtxt - 14) / 2
    c = [borda(W, H, t),
         T(x0, 30, '>_', 'M', 20, t['mute'], esp=.5),
         T(x0 + medir('>_ ', 'M', 20, .5), 30, txt, 'M', 20, t['fg'], esp=.5),
         f'<rect x="{x0 + wtxt + 4:.1f}" y="15" width="9" height="17" fill="{t["fg"]}" class="blink"/>']
    return montar('terminal-' + tema, W, H, ''.join(c), '>_ ' + txt, fundo=t['bg'])


def botao(tema, arq, rot, destaque):
    t = TEMAS[tema]
    H, tam = 36, 19
    label = rot + '  ↗'
    w = int(medir(label, 'M', tam, 1.5) + 34)
    if destaque:
        c = [f'<rect width="{w}" height="{H}" fill="{t["fg"]}"/>', T(17, 24, label, 'M', tam, t['bg'], esp=1.5)]
    else:
        c = [f'<rect x=".5" y=".5" width="{w - 1}" height="{H - 1}" fill="{t["bg"]}" stroke="{t["fg"]}"/>',
             T(17, 24, label, 'M', tam, t['fg'], esp=1.5)]
    return montar(f'btn-{arq}-{tema}', w, H, ''.join(c), rot)


def secao(tema, arq, num, titulo, rot):
    t = TEMAS[tema]
    H = 44
    c = [T(0, 30, num, 'M', 24, t['mute'], esp=1),
         T(32, 30, '//', 'M', 24, t['mute']),
         T(62, 30, titulo, 'M', 28, t['fg'], esp=4)]
    x1 = 62 + medir(titulo, 'M', 28, 4) + 16
    x2 = W - medir(rot, 'M', 16, 2) - 16
    c.append(f'<line x1="{x1:.1f}" y1="23.5" x2="{x2:.1f}" y2="23.5" stroke="{t["line"]}"/>')
    c.append(T(W, 29, rot, 'M', 16, t['mute'], esp=2, anchor='end'))
    return montar(f'sec-{arq}-{tema}', W, H, ''.join(c), f'{num} // {titulo}')


def sobre(tema):
    t = TEMAS[tema]
    pad, cap, art = 34, 78, 130
    tam, lh = 17.5, 28
    xt = pad + cap + 14
    larg = [W - xt - art - 60] * 3 + [W - 2 * pad - art - 40] + [W - 2 * pad]
    linhas = quebrar(CONTEUDO['bio'][1:], 'R', tam, larg)   # a 1ª letra vira a capitular
    c = [halftone('capR', pad - 4, pad - 6, cap + 8, t['fg'])]
    y = pad + 22
    for i, ln in enumerate(linhas):
        c.append(T(xt if i < 3 else pad, y, ln, 'R', tam, t['fg']))
        y += lh
    ax, ay = W - pad - art, pad
    c.append(halftone('floppy', ax, ay, art, t['fg']))
    c.append(cantos(ax - 6, ay + 2, art + 12, art - 4, 10, t['trk']))
    y = max(y, ay + art) + 26
    c.append(f'<line x1="{pad}" y1="{y - 20}" x2="{W - pad}" y2="{y - 20}" stroke="{t["line"]}"/>')
    y += 8
    for k, v in CONTEUDO['ficha']:
        c.append(T(pad, y, k, 'M', 18, t['mute'], esp=2.5))
        c.append(T(pad + 190, y, v, 'R', 17, t['fg']))
        y += 34
    H = int(y + pad - 20)
    alt = CONTEUDO['bio'] + ' ' + ' '.join(f'{k.capitalize()}: {v}.' for k, v in CONTEUDO['ficha'])
    return montar('sobre-' + tema, W, H, borda(W, H, t) + ''.join(c), alt, fundo=t['bg'])


def icones(tema):
    t = TEMAS[tema]
    ic = json.load(open(os.path.join(AQUI, 'src', 'icones.json')))
    nomes = CONTEUDO['icones']
    s, gap = 50, 9
    x = (W - (len(nomes) * s + (len(nomes) - 1) * gap)) / 2
    c = []
    for n in nomes:
        c.append(f'<rect x="{x + .5:.1f}" y=".5" width="{s - 1}" height="{s - 1}" fill="none" stroke="{t["line"]}"/>')
        c.append(f'<g transform="translate({x + 13:.1f},13)" fill="{t["fg"]}"><path d="{ic[n]["path"]}"/></g>')
        x += s + gap
    return montar('icones-' + tema, W, s, ''.join(c), 'Ferramentas: ' + ', '.join(ic[n]['title'] for n in nomes))


def tags(tema):
    t = TEMAS[tema]
    y, c = 4, []
    tam, h, gap = 17, 30, 8
    for cat, itens in CONTEUDO['tags']:
        c.append(T(0, y + 14, cat, 'M', 17, t['fg'], esp=2.5))
        y += 24
        x = 0
        for it in itens:
            w = medir(it, 'M', tam, 1) + 22
            if x + w > W:
                x, y = 0, y + h + gap
            c.append(f'<rect x="{x + .5:.1f}" y="{y + .5}" width="{w - 1:.1f}" height="{h - 1}" fill="none" stroke="{t["line"]}"/>')
            c.append(T(x + 11, y + 20, it, 'M', tam, t['mute'], esp=1))
            x += w + gap
        y += h + 24
    alt = ' '.join(f'{cat.capitalize()}: ' + ', '.join(i) + '.' for cat, i in CONTEUDO['tags'])
    return montar('tags-' + tema, W, int(y - 16), ''.join(c), alt)


# --------------------------------------------- telas de PSP (repos públicos)
SCAN = ('<defs><pattern id="sl" width="4" height="3" patternUnits="userSpaceOnUse">'
        '<rect width="4" height="1" fill="#000" opacity=".35"/></pattern>'
        '<radialGradient id="vg" cx=".5" cy=".45" r=".75"><stop offset=".6" stop-color="#000" stop-opacity="0"/>'
        '<stop offset="1" stop-color="#000" stop-opacity=".6"/></radialGradient></defs>')


def tela(arq, idx, caminho, titulo, desc, stack, nota, w=410, h=230):
    """Cartão no formato da tela do PSP do portfólio."""
    fg, mute = '#ffffff', 'rgba(255,255,255,.6)'
    c = [SCAN, f'<rect width="{w}" height="{h}" fill="#070707"/>',
         T(w - 16, h - 18, '%02d' % idx, 'M', 170, fg, anchor='end', extra='opacity=".05"'),
         T(20, 32, caminho, 'M', 17, mute, esp=.5),
         T(w - 20, 32, '↗', 'M', 20, fg, anchor='end'),
         T(20, 92, titulo, 'I', 30, fg, esp=-.4)]
    yy = 124
    for ln in quebrar(desc, 'M', 19, [w - 44])[:3]:
        c.append(T(21, yy, ln, 'M', 19, mute, esp=.2))
        yy += 21
    c.append(T(21, h - 20, stack, 'M', 16, fg, esp=1))
    if nota:
        c.append(T(w - 20, h - 20, nota, 'M', 16, fg, esp=1, anchor='end'))
    c.append(f'<rect width="{w}" height="{h}" fill="url(#sl)"/>')
    c.append(f'<rect width="{w}" height="{h}" fill="url(#vg)"/>')
    c.append(f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" fill="none" stroke="#333"/>')
    return montar('card-' + arq, w, h, ''.join(c), f'{titulo}: {desc}')


def andamento(tema):
    """Os privados numa lista enxuta: nome, uma linha e o estado."""
    t = TEMAS[tema]
    pad, lh = 24, 66
    c = []
    y = 8
    for k, (ti, de, st) in enumerate(CONTEUDO['andamento']):
        if k:
            c.append(f'<line x1="{pad}" y1="{y:.1f}" x2="{W - pad}" y2="{y:.1f}" stroke="{t["line"]}"/>')
        c.append(T(pad, y + 30, '%02d' % (k + 1), 'M', 18, t['mute'], esp=1))
        c.append(T(pad + 40, y + 30, ti, 'I', 21, t['fg']))
        c.append(T(W - pad, y + 30, st, 'M', 16, t['mute'], esp=1.5, anchor='end'))
        c.append(T(pad + 40, y + 52, de, 'M', 17, t['mute'], esp=.2))
        y += lh
    c.append(T(pad, y + 22, CONTEUDO['andamento_nota'], 'M', 16, t['mute'], esp=.4))
    H = int(y + 40)
    alt = ' '.join(f'{ti}: {de}' for ti, de, _ in CONTEUDO['andamento']) + ' ' + CONTEUDO['andamento_nota']
    return montar('andamento-' + tema, W, H, borda(W, H, t) + ''.join(c), alt, fundo=t['bg'])


def contato(tema):
    t = TEMAS[tema]
    H = 220
    a, b = CONTEUDO['contato']
    tam, cut = 66, 128
    wa, wb = medir(a, 'I', tam), medir(b, 'I', tam)
    x = (W - (wa + cut + wb + 20)) / 2
    cx = x + wa + 10
    c = [borda(W, H, t),
         T(x + wa, 112, a, 'I', tam, t['fg'], esp=-1, anchor='end'),
         halftone('at', cx, 28, cut, t['fg']),
         cantos(cx - 4, 32, cut + 8, cut - 4, 10, t['trk']),
         T(cx + cut + 10, 112, b, 'I', tam, t['fg'], esp=-1),
         T(W / 2, 186, CONTEUDO['contato_txt'], 'M', 18, t['mute'], esp=.5, anchor='middle')]
    return montar('contato-' + tema, W, H, ''.join(c), f'{a} @ {b} ' + CONTEUDO['contato_txt'], fundo=t['bg'])


def rodape(tema):
    t = TEMAS[tema]
    a, b = CONTEUDO['rodape']
    c = [f'<line x1="0" y1=".5" x2="{W}" y2=".5" stroke="{t["line"]}"/>',
         T(0, 27, a, 'M', 17, t['mute'], esp=2),
         T(W, 27, b, 'M', 17, t['mute'], esp=1.5, anchor='end')]
    return montar('rodape-' + tema, W, 40, ''.join(c), f'{a} · {b}')


def main():
    os.makedirs(SAIDA, exist_ok=True)
    for f in os.listdir(SAIDA):                      # sem sobras de versões antigas
        if f.endswith('.svg'):
            os.remove(os.path.join(SAIDA, f))
    tam = {}
    for tema in TEMAS:
        tam['banner-' + tema] = banner(tema)
        tam['terminal-' + tema] = terminal(tema)
        for arq, rot, d in CONTEUDO['botoes']:
            tam[f'btn-{arq}-{tema}'] = botao(tema, arq, rot, d)
        for s in CONTEUDO['secoes']:
            tam[f'sec-{s[0]}-{tema}'] = secao(tema, *s)
        tam['sobre-' + tema] = sobre(tema)
        tam['icones-' + tema] = icones(tema)
        tam['tags-' + tema] = tags(tema)
        tam['andamento-' + tema] = andamento(tema)
        tam['contato-' + tema] = contato(tema)
        tam['rodape-' + tema] = rodape(tema)
    for i, r in enumerate(CONTEUDO['abertos']):
        tam['card-' + r[0]] = tela(r[0], i + 1, *r[1:])
    print(f'{len(tam)} arquivos, {sum(tam.values()) / 1024:.0f} KB; maiores: '
          + ', '.join(f'{k} {v // 1024}KB' for k, v in sorted(tam.items(), key=lambda kv: -kv[1])[:3]))


if __name__ == '__main__':
    main()
