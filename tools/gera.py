"""Gera todas as imagens do README do perfil (assets/*.svg).

Estética: a mesma do portfólio (exgde.github.io): preto e branco, recortes
em halftone, camada de "tracking" cinza, VT323 para o HUD e itálico para os
títulos. Cada peça sai em duas versões, -dark e -light (o "inverter" do
site vira o tema do GitHub). Os cartões de projeto são telas de PSP e são
pretos nos dois temas, então saem numa versão só.

    python3 tools/gera.py          (a partir da raiz do repositório)

Todo o texto fica em CONTEUDO, logo abaixo. Dependências: fonttools,
brotli, Pillow.
"""
import base64
import io
import json
import math
import os
import random
import re
from xml.sax.saxutils import escape

from fontTools.subset import Options, Subsetter
from fontTools.ttLib import TTFont
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(AQUI, '..', 'assets')
W = 840

# ------------------------------------------------------------------ conteúdo
CONTEUDO = {
    'tag': '#JOAOBYSS',
    'nome': 'joaobyss',
    'funcao': 'IA LOCAL  /  AUTOMAÇÃO  /  JOGOS',
    'status': 'ONLINE · ABERTO A VAGAS JR',
    'terminal': 'ligando modelos de IA a ferramentas reais, e fazendo jogos nas horas vagas',
    'botoes': [  # (arquivo, rótulo, destaque)
        ('portfolio', 'PORTFÓLIO', True),
        ('linkedin', 'LINKEDIN', False),
        ('email', 'E-MAIL', False),
        ('itch', 'ITCH.IO', False),
    ],
    'secoes': [  # (arquivo, número, título, rótulo da direita)
        ('sobre', '01', 'SOBRE', 'PLAYER.INFO'),
        ('stack', '02', 'STACK', 'INVENTORY'),
        ('projetos', '03', 'PROJETOS', 'SAVE.DATA'),
        ('jogos', '04', 'JOGOS E CÓDIGO ABERTO', 'UMD.LIST'),
        ('contato', '05', 'CONTATO', 'LINK.CABLE'),
    ],
    'bio': ('Rodo modelos de linguagem na minha própria máquina desde 2023. Hoje meu foco '
            'é automação e integração inteligente: ligar modelos a ferramentas, dados e '
            'rotinas reais, inclusive via MCP. Antes disso, e até hoje, faço jogos e mods. '
            'No momento, o WW1-Thriller, um terror em terceira pessoa na Unreal Engine 5.'),
    'ficha': [
        ('CLASSE', 'AI Engineer / Automação (júnior)'),
        ('FOCO', 'IA local, MCP, agentes e integração'),
        ('XP', 'Rodando LLMs localmente desde 2023'),
        ('BASE', 'Ciência da Computação, UFJ'),
        ('SIDE QUEST', 'Jogos e mods desde 2019 (Unity e Unreal)'),
        ('COMBUSTÍVEL', 'Café, silêncio e uma GPU'),
    ],
    'icones': ['claude', 'python', 'typescript', 'nodedotjs', 'docker', 'sqlite', 'mysql',
               'git', 'swift', 'dotnet', 'unity', 'unrealengine', 'blender'],
    'frase': 'ferramenta boa é a que roda na sua máquina.',
    'tags': [
        ('IA E DADOS', ['LLMs locais', 'MCP', 'Claude Code', 'Contexto e parâmetros', 'SQLite', 'MySQL']),
        ('AUTOMAÇÃO E INTEGRAÇÃO', ['Node.js', 'TypeScript', 'Python', 'Docker', 'Playwright', 'Remotion', 'Git']),
        ('JOGOS E 3D', ['Unreal Engine 5', 'Blueprint', 'Unity', 'Blender', 'C#', 'Swift']),
    ],
    # cartões: (arquivo, título, descrição, stack, status, ação)
    'projetos': [
        ('cutscene', 'CUTSCENE-LOADER', 'Animação 3D a partir de vídeo comum, sem mocap. Exporta BVH para o Blender.',
         'VÍDEO · BVH · BLENDER', 'PRÉ-ALPHA', None),
        ('painel', 'Painel com MCP próprio', 'Servidor MCP que dá estado real ao Claude, com Qwen local como segundo parecer.',
         'MCP · CLAUDE · QWEN LOCAL', 'EM PREPARAÇÃO', None),
        ('videos', 'Fábrica de vídeos com IA', 'Roteiro, voz local e animação 3D por código, com aprovação antes de publicar.',
         'ROTEIRO · VOZ LOCAL · 3D', 'EM PREPARAÇÃO', None),
        ('prospeccao', 'Pipeline de prospecção', 'Busca, página de demonstração e fila de mensagens, com limite de custo e aprovação humana.',
         'BUSCA · DEMO · FILA', 'EM PREPARAÇÃO', None),
    ],
    'destaque': ('casa-acessivel', 'Casa Acessível', 'Casa e banheiro para cadeira de rodas, em realidade virtual.',
                 'UNREAL ENGINE 5.8 · BLENDER · PYTHON · 2026', 'REALIDADE VIRTUAL'),
    'jogos': [
        ('ww1', 'WW1-Thriller', 'Terror em terceira pessoa, todo em Blueprint. Em desenvolvimento.',
         'UNREAL ENGINE 5.8 · BLUEPRINT', 'EM DESENVOLVIMENTO', None),
        ('goldspotting', 'Goldspotting', 'Meu primeiro jogo lançado de verdade. Fiz na Unity e está no itch.io.',
         'UNITY · ITCH.IO · 2026', 'LANÇADO', 'JOGAR'),
        ('button-prompts', 'Button Prompts', 'Troca os ícones de botão do OOT (Switch 2) por PlayStation, Xbox e Steam Deck.',
         'MOD · ROMFS · LAYEREDFS', 'CÓDIGO ABERTO', 'ABRIR'),
        ('teclado-mouse', 'Teclado + Mouse', 'Pra jogar OOT no Lichii de teclado e mouse. Troca até os ícones de controle.',
         'PYTHON · POWERSHELL · EMULAÇÃO', 'CÓDIGO ABERTO', 'ABRIR'),
        ('adega', 'Adega', 'Meu CrossOver caseiro: app pra macOS que roda programas do Windows com Wine.',
         'SWIFT · SWIFTUI · WINE', 'CÓDIGO ABERTO', 'ABRIR'),
        ('biblioteca-sql', 'Biblioteca SQL', 'Trabalho de Banco de Dados da UFJ: modelo MySQL de uma biblioteca, com 12 consultas.',
         'MYSQL · SQL · MODELAGEM', 'CÓDIGO ABERTO', 'ABRIR'),
    ],
    'contato': ['fale', 'comigo.'],
    'contato_txt': 'procuro vaga júnior em AI engineering ou automação. também topo freela e colaboração.',
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


_seq = [0]


def rotulo_trk(x, y, ident, cor, tam=13):
    """TRK_nn com a confiança trocando sozinha (4 valores em ciclo)."""
    _seq[0] += 1
    rnd = random.Random(_seq[0])
    confs = ['0.%03d' % rnd.randint(918, 989) for _ in range(4)]
    out = [T(x, y, ident, 'M', tam, cor)]
    dx = medir(ident + '  ', 'M', tam)
    for k, c in enumerate(confs):
        out.append(T(x + dx, y, c, 'M', tam, cor,
                     extra=f'style="animation:cyc 3.2s linear infinite;animation-delay:{-k * .8:.1f}s;opacity:{1 if k == 0 else 0}"'))
    return ''.join(out)


def moldura(w, h, t, cantoL=14, x=0.5, y=0.5):
    return (f'<rect x="{x}" y="{y}" width="{w - 2 * x}" height="{h - 2 * y}" fill="none" stroke="{t["line"]}"/>'
            + cantos(x + 4, y + 4, w - 2 * x - 8, h - 2 * y - 8, cantoL, t['fg']))


# ================================================================ peças
def banner(tema):
    t = TEMAS[tema]
    m = json.load(open(os.path.join(AQUI, 'src', 'maos.json')))
    H = 400
    y0, ox, oy = 270, (W - m['w']) / 2, 34   # recorte vertical da imagem original
    pts = [(x + ox, y - y0 + oy, v) for x, y, v in m['pts']]
    meio = W / 2
    esq = [p for p in pts if p[0] < meio]
    dirt = [p for p in pts if p[0] >= meio]
    rnd = random.Random(7)
    dots = [f'<g fill="{t["fg"]}">']
    for x, y, v in pts:
        cls = ' class="tw"' if rnd.random() < .05 else ''
        sty = f' style="animation-delay:{-rnd.random() * 4:.2f}s"' if cls else ''
        dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{1.05 + .55 * math.sqrt(v):.2f}"{cls}{sty}/>')
    dots.append('</g>')

    def bbox(ps, pad=8):
        xs, ys = [p[0] for p in ps], [p[1] for p in ps]
        return min(xs) - pad, min(ys) - pad, max(xs) - min(xs) + 2 * pad, max(ys) - min(ys) + 2 * pad
    ponta_e = max(esq, key=lambda p: p[0])
    ponta_d = min(dirt, key=lambda p: p[0])
    c = []
    c.append(moldura(W, H, t))
    # HUD de cima
    c.append(T(22, 26, CONTEUDO['tag'], 'M', 15, t['mute'], esp=1.5))
    c.append(f'<circle cx="{W - 22 - medir(CONTEUDO["status"], "M", 15, 1.2) - 12}" cy="21.5" r="3.5" fill="{t["fg"]}" class="pulse"/>')
    c.append(T(W - 22, 26, CONTEUDO['status'], 'M', 15, t['mute'], esp=1.2, anchor='end'))
    c.append(f'<line x1="0" y1="38" x2="{W}" y2="38" stroke="{t["line"]}"/>')
    # mãos + tracking
    c.append(''.join(dots))
    for i, ps in enumerate((esq, dirt)):
        bx, by, bw, bh = bbox(ps)
        c.append(cantos(bx, by, bw, bh, 12, t['trk']))
        c.append(rotulo_trk(bx, by - 6, 'TRK_0%d' % (i + 1), t['trk'], 12))
    # a faísca entre os dedos
    ex, ey, dx_, dy_ = ponta_e[0] + 5, ponta_e[1], ponta_d[0] - 5, ponta_d[1]
    mx, my = (ex + dx_) / 2, (ey + dy_) / 2
    c.append(f'<line x1="{ex:.1f}" y1="{ey:.1f}" x2="{dx_:.1f}" y2="{dy_:.1f}" stroke="{t["trk"]}" stroke-width="1" stroke-dasharray="2 3"/>')
    for px, py in ((ex, ey), (dx_, dy_)):
        c.append(f'<rect x="{px - 2.5:.1f}" y="{py - 2.5:.1f}" width="5" height="5" fill="none" stroke="{t["trk"]}"/>')
    c.append(f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="3" fill="{t["fg"]}" class="spark"/>')
    c.append(f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="9" fill="none" stroke="{t["fg"]}" class="ring"/>')
    c.append(T(mx, my - 16, 'MCP', 'M', 12, t['trk'], anchor='middle', esp=1))
    # varredura
    c.append(f'<rect x="0" y="40" width="1" height="{250 - 40}" fill="{t["fg"]}" opacity=".18" class="scan"/>')
    # nós soltos
    for k in range(6):
        nx, ny = rnd.uniform(40, W - 40), rnd.uniform(50, 380)
        c.append(f'<circle cx="{nx:.0f}" cy="{ny:.0f}" r="2.2" fill="none" stroke="{t["trk"]}" class="drift" style="animation-delay:{-k * 1.7:.1f}s"/>')
    # nome e função
    c.append(T(W / 2, 322, CONTEUDO['nome'], 'I', 76, t['fg'], esp=-1.5, anchor='middle'))
    c.append(T(W / 2, 354, CONTEUDO['funcao'], 'M', 18, t['mute'], esp=3, anchor='middle'))
    c.append(f'<line x1="0" y1="{H - 30}" x2="{W}" y2="{H - 30}" stroke="{t["line"]}"/>')
    c.append(T(22, H - 10, 'exgde / README.md', 'M', 14, t['mute'], esp=1))
    c.append(T(W - 22, H - 10, 'CRIAÇÃO_DE_ADÃO.DOT  ·  1684 PTS', 'M', 14, t['mute'], esp=1, anchor='end'))
    css = ('@keyframes tw{0%,100%{opacity:1}50%{opacity:.15}}.tw{animation:tw 2.6s ease-in-out infinite}'
           '@keyframes pulse{0%,100%{opacity:1}50%{opacity:.2}}.pulse{animation:pulse 1.6s ease-in-out infinite}'
           '.spark{animation:pulse 1.2s ease-in-out infinite}'
           '@keyframes ring{0%{transform:scale(.4);opacity:.9}100%{transform:scale(2.2);opacity:0}}'
           f'.ring{{transform-origin:{mx:.1f}px {my:.1f}px;animation:ring 2.4s ease-out infinite}}'
           f'@keyframes scan{{0%{{transform:translateX(0)}}100%{{transform:translateX({W}px)}}}}'
           '.scan{animation:scan 7s linear infinite}'
           '@keyframes drift{0%,100%{transform:translate(0,0)}50%{transform:translate(9px,-6px)}}'
           '.drift{animation:drift 9s ease-in-out infinite}')
    return montar('banner-' + tema, W, H, ''.join(c),
                  'joaobyss: IA local, automação e jogos. Duas mãos em pontos quase se tocando.', css, t['bg'])


def terminal(tema):
    t = TEMAS[tema]
    H = 46
    txt = CONTEUDO['terminal']
    full = '>_ ' + txt
    wtxt = medir(full, 'M', 20, .5)
    x0 = (W - wtxt - 14) / 2
    c = [moldura(W, H, t, 8),
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
    H = 48
    c = [T(0, 31, num, 'M', 24, t['mute'], esp=1),
         T(32, 31, '//', 'M', 24, t['line'] if tema == 'dark' else '#b0b0b0'),
         T(62, 31, titulo, 'M', 28, t['fg'], esp=4)]
    x1 = 62 + medir(titulo, 'M', 28, 4) + 14
    x2 = W - medir(rot, 'M', 16, 2) - 16
    c.append(f'<rect x="{x1:.1f}" y="22" width="6" height="6" fill="{t["fg"]}"/>')
    c.append(f'<line x1="{x1 + 10:.1f}" y1="25" x2="{x2:.1f}" y2="25" stroke="{t["mute"]}" stroke-width="1"/>')
    c.append(f'<line x1="{x2 - 18:.1f}" y1="21" x2="{x2 - 18:.1f}" y2="29" stroke="{t["mute"]}"/>')
    c.append(T(W, 30, rot, 'M', 16, t['mute'], esp=2, anchor='end'))
    c.append(f'<line x1="0" y1="{H - .5}" x2="{W}" y2="{H - .5}" stroke="{t["line"]}"/>')
    return montar(f'sec-{arq}-{tema}', W, H, ''.join(c), f'{num} // {titulo}')


def sobre(tema):
    t = TEMAS[tema]
    pad, cap = 34, 78
    art = 150
    tam, lh = 17.5, 28
    xt = pad + cap + 14
    bio = CONTEUDO['bio'][1:]                      # a 1ª letra vira a capitular
    larg = [W - xt - art - 60] * 3 + [W - 2 * pad - art - 40] * 1 + [W - 2 * pad]
    linhas = quebrar(bio, 'R', tam, larg)
    c = [moldura(W, 10, t)]                        # placeholder, refeito no fim
    c = []
    y = pad + 22
    c.append(halftone('capR', pad - 4, pad - 6, cap + 8, t['fg']))
    for i, ln in enumerate(linhas):
        x = xt if i < 3 else pad
        c.append(T(x, y, ln, 'R', tam, t['fg']))
        y += lh
    # recorte à direita com tracking
    ax, ay = W - pad - art, pad - 4
    c.append(halftone('floppy', ax, ay, art, t['fg']))
    c.append(cantos(ax - 6, ay + 4, art + 12, art - 2, 12, t['trk']))
    c.append(rotulo_trk(ax - 6, ay - 2, 'TRK_03', t['trk'], 12))
    y = max(y, ay + art + 10) + 22
    c.append(f'<line x1="{pad}" y1="{y - 18}" x2="{W - pad}" y2="{y - 18}" stroke="{t["line"]}"/>')
    for k, v in CONTEUDO['ficha']:
        c.append(f'<rect x="{pad}" y="{y - 10}" width="6" height="6" fill="{t["fg"]}"/>')
        c.append(T(pad + 20, y, k, 'M', 18, t['mute'], esp=2.5))
        lead_x = pad + 20 + medir(k, 'M', 18, 2.5) + 10
        c.append(f'<line x1="{lead_x:.1f}" y1="{y - 4}" x2="{pad + 214}" y2="{y - 4}" stroke="{t["line"]}" stroke-dasharray="1 4"/>')
        c.append(T(pad + 226, y, v, 'R', 17, t['fg']))
        y += 36
    H = int(y + pad - 14)
    alt = 'Sobre: ' + CONTEUDO['bio'] + ' ' + '; '.join(f'{k.lower()}: {v}' for k, v in CONTEUDO['ficha'])
    return montar('sobre-' + tema, W, H, moldura(W, H, t) + ''.join(c), alt, fundo=t['bg'])


def icones(tema):
    t = TEMAS[tema]
    ic = json.load(open(os.path.join(AQUI, 'src', 'icones.json')))
    nomes = CONTEUDO['icones']
    s, gap = 50, 9
    tot = len(nomes) * s + (len(nomes) - 1) * gap
    x = (W - tot) / 2
    H = s + 2
    c = []
    for k, n in enumerate(nomes):
        c.append(f'<rect x="{x + .5:.1f}" y="1.5" width="{s - 1}" height="{s - 1}" fill="{t["bg"]}" stroke="{t["line"]}"/>')
        c.append(cantos(x + 3, 4, s - 6, s - 6, 5, t['mute']))
        sc = 24 / 24
        c.append(f'<g transform="translate({x + 13:.1f},14) scale({sc})" fill="{t["fg"]}"><path d="{ic[n]["path"]}"/></g>')
        x += s + gap
    return montar('icones-' + tema, W, H, ''.join(c),
                  'Ferramentas: ' + ', '.join(ic[n]['title'] for n in nomes))


def frase(tema):
    t = TEMAS[tema]
    H = 96
    tam = 30
    w = medir(CONTEUDO['frase'], 'I', tam, -.5)
    c = [moldura(W, H, t, 10), T(W / 2, 58, CONTEUDO['frase'], 'I', tam, t['fg'], esp=-.5, anchor='middle')]
    for sx in (W / 2 - w / 2 - 58, W / 2 + w / 2 + 18):
        c.append(halftone('star', sx, 28, 40, t['fg']))
    return montar('frase-' + tema, W, H, ''.join(c), CONTEUDO['frase'], fundo=t['bg'])


def tags(tema):
    t = TEMAS[tema]
    y, c = 4, []
    tam, h, gap = 17, 30, 8
    for cat, itens in CONTEUDO['tags']:
        c.append(f'<rect x="0" y="{y + 6}" width="6" height="6" fill="{t["fg"]}"/>')
        c.append(T(16, y + 14, cat, 'M', 17, t['fg'], esp=2.5))
        y += 24
        x = 0
        for it in itens:
            w = medir(it, 'M', tam, 1) + 22
            if x + w > W:
                x, y = 0, y + h + gap
            c.append(f'<rect x="{x + .5:.1f}" y="{y + .5}" width="{w - 1:.1f}" height="{h - 1}" fill="none" stroke="{t["line"]}"/>')
            c.append(T(x + 11, y + 20, it, 'M', tam, t['mute'], esp=1))
            x += w + gap
        y += h + 26
    H = int(y - 16)
    alt = '; '.join(f'{cat}: ' + ', '.join(i) for cat, i in CONTEUDO['tags'])
    return montar('tags-' + tema, W, H, ''.join(c), alt)


# ------------------------------------------------- telas de PSP (cartões)
SCAN = ('<defs><pattern id="sl" width="4" height="3" patternUnits="userSpaceOnUse">'
        '<rect width="4" height="1" fill="#000" opacity=".45"/></pattern>'
        '<radialGradient id="vg" cx=".5" cy=".45" r=".75"><stop offset=".55" stop-color="#000" stop-opacity="0"/>'
        '<stop offset="1" stop-color="#000" stop-opacity=".75"/></radialGradient>'
        '<linearGradient id="bt" x1="0" y1="0" x2="0" y2="1"><stop offset=".35" stop-color="#000" stop-opacity="0"/>'
        '<stop offset="1" stop-color="#000" stop-opacity=".9"/></linearGradient></defs>')


def tela(arq, idx, tot, titulo, desc, stack, status, acao, w=410, h=250, img=None):
    """Cartão no formato da tela do PSP do portfólio."""
    fg, mute = '#ffffff', 'rgba(255,255,255,.62)'
    c = [SCAN, f'<rect width="{w}" height="{h}" fill="#070707"/>']
    if img:
        c.append(f'<image href="data:image/jpeg;base64,{img}" xlink:href="data:image/jpeg;base64,{img}" '
                 f'width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice"/>')
        c.append(f'<rect width="{w}" height="{h}" fill="url(#bt)"/>')
    else:
        c.append(T(w - 18, h - 22, '%02d' % idx, 'M', 190, fg, anchor='end', extra='opacity=".07"'))
    # topo
    topo = ('▶ ' + acao) if acao else '■ PRIVADO'
    c.append(T(20, 32, topo, 'M', 19, fg, esp=1))
    c.append(T(w - 20, 32, '%02d/%02d' % (idx, tot), 'M', 19, fg, esp=1, anchor='end'))
    if img:
        c.append(T(22, h - 74, titulo, 'I', 40, fg, esp=-.5))
        c.append(T(23, h - 44, desc, 'M', 19, mute, esp=.3))
        c.append(T(23, h - 18, stack, 'M', 17, fg, esp=1))
    else:
        c.append(T(20, 98, titulo, 'I', 30 if medir(titulo, 'I', 30) < w - 40 else 25, fg, esp=-.4))
        ls = quebrar(desc, 'M', 19, [w - 48])
        yy = 128
        for k, ln in enumerate(ls[:3]):
            c.append(T(21, yy, ln, 'M', 19, mute, esp=.2))
            yy += 21
        lw = medir(ls[min(len(ls), 3) - 1], 'M', 19, .2)
        c.append(f'<rect x="{21 + lw + 3:.1f}" y="{yy - 21 - 14}" width="9" height="16" fill="{fg}" class="blink"/>')
        c.append(T(21, h - 20, stack, 'M', 16, fg, esp=1))
    sw = medir(status, 'M', 15, 1) + 16
    c.append(f'<rect x="{w - 20 - sw:.1f}" y="{(h - 62) if not img else 14 + 26}" width="{sw:.1f}" height="22" fill="none" stroke="rgba(255,255,255,.45)"/>')
    c.append(T(w - 20 - sw + 8, ((h - 62) if not img else 40) + 16, status, 'M', 15, fg, esp=1))
    c.append(f'<rect width="{w}" height="{h}" fill="url(#sl)"/>')
    c.append(f'<rect width="{w}" height="{h}" fill="url(#vg)"/>')
    c.append(f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" fill="none" stroke="#3a3a3a"/>')
    c.append(cantos(6, 6, w - 12, h - 12, 10, 'rgba(255,255,255,.5)'))
    alt = f'{titulo}: {desc} {stack.title()}. {status.capitalize()}.'
    return montar('card-' + arq, w, h, ''.join(c), alt)


def contato(tema):
    t = TEMAS[tema]
    H = 250
    a, b = CONTEUDO['contato']
    tam, cut = 70, 138
    wa, wb = medir(a, 'I', tam), medir(b, 'I', tam)
    tot = wa + cut + wb + 2 * 10
    x = (W - tot) / 2
    c = [moldura(W, H, t)]
    c.append(T(x + wa, 120, a, 'I', tam, t['fg'], esp=-1, anchor='end'))
    cx = x + wa + 10
    c.append(halftone('at', cx, 30, cut, t['fg']))
    c.append(cantos(cx - 4, 34, cut + 8, cut - 4, 11, t['trk']))
    c.append(rotulo_trk(cx - 4, 28, 'TRK_06', t['trk'], 12))
    c.append(T(cx + cut + 10, 120, b, 'I', tam, t['fg'], esp=-1))
    c.append(halftone('cursor', W - 84, 20, 60, t['fg']))
    c.append(halftone('chip', 16, 14, 56, t['fg'], .9))
    c.append(T(W / 2, 205, CONTEUDO['contato_txt'], 'M', 19, t['mute'], esp=.6, anchor='middle'))
    return montar('contato-' + tema, W, H, ''.join(c),
                  f'{a} @ {b} ' + CONTEUDO['contato_txt'], fundo=t['bg'])


def rodape(tema):
    t = TEMAS[tema]
    H = 40
    a, b = CONTEUDO['rodape']
    c = [f'<line x1="0" y1=".5" x2="{W}" y2=".5" stroke="{t["line"]}"/>',
         T(0, 27, a, 'M', 17, t['mute'], esp=2),
         T(W, 27, b, 'M', 17, t['mute'], esp=1.5, anchor='end'),
         f'<rect x="{medir(a, "M", 17, 2) + 6:.1f}" y="14" width="8" height="14" fill="{t["mute"]}" class="blink"/>']
    return montar('rodape-' + tema, W, H, ''.join(c), f'{a} · {b}')


def capa_jpeg(w, h):
    im = Image.open(os.path.join(AQUI, 'src', 'casa-acessivel.jpg')).convert('RGB')
    r = max(w * 2 / im.width, h * 2 / im.height)
    im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    l, tp = (im.width - w * 2) // 2, (im.height - h * 2) // 2
    im = im.crop((l, tp, l + w * 2, tp + h * 2))
    b = io.BytesIO()
    im.save(b, 'JPEG', quality=68, optimize=True, progressive=True)
    return base64.b64encode(b.getvalue()).decode()


def main():
    os.makedirs(SAIDA, exist_ok=True)
    tamanhos = {}
    for tema in TEMAS:
        tamanhos['banner-' + tema] = banner(tema)
        tamanhos['terminal-' + tema] = terminal(tema)
        for arq, rot, d in CONTEUDO['botoes']:
            tamanhos[f'btn-{arq}-{tema}'] = botao(tema, arq, rot, d)
        for s in CONTEUDO['secoes']:
            tamanhos[f'sec-{s[0]}-{tema}'] = secao(tema, *s)
        tamanhos['sobre-' + tema] = sobre(tema)
        tamanhos['icones-' + tema] = icones(tema)
        tamanhos['frase-' + tema] = frase(tema)
        tamanhos['tags-' + tema] = tags(tema)
        tamanhos['contato-' + tema] = contato(tema)
        tamanhos['rodape-' + tema] = rodape(tema)
    n = len(CONTEUDO['projetos'])
    for i, (arq, ti, de, st, sts, ac) in enumerate(CONTEUDO['projetos']):
        tamanhos['card-' + arq] = tela(arq, i + 1, n, ti, de, st, sts, ac)
    jg = CONTEUDO['jogos']
    arq, ti, de, st, sts = CONTEUDO['destaque']
    tamanhos['card-' + arq] = tela(arq, 1, len(jg) + 1, ti, de, st, sts, 'VER NO PSP', w=W, h=330, img=capa_jpeg(W, 330))
    for i, (arq, ti, de, st, sts, ac) in enumerate(jg):
        tamanhos['card-' + arq] = tela(arq, i + 2, len(jg) + 1, ti, de, st, sts, ac)
    total = sum(tamanhos.values())
    print(f'{len(tamanhos)} arquivos, {total / 1024:.0f} KB no total; maior: '
          + ', '.join(f'{k} {v // 1024}KB' for k, v in sorted(tamanhos.items(), key=lambda kv: -kv[1])[:4]))


if __name__ == '__main__':
    main()
