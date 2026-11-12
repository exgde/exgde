<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://capsule-render.vercel.app/api?type=rect&color=2B2B2B&height=200&section=header&text=Jo%C3%A3o%20Bernardes&fontSize=64&fontColor=E8D5B7&desc=AI%20engineering%20%E2%80%A2%20automa%C3%A7%C3%A3o%20%E2%80%A2%20IA%20local&descSize=22&descAlignY=74&fontAlignY=42">
  <img src="https://capsule-render.vercel.app/api?type=rect&color=F5EFE6&height=200&section=header&text=Jo%C3%A3o%20Bernardes&fontSize=64&fontColor=5C3A21&desc=AI%20engineering%20%E2%80%A2%20automa%C3%A7%C3%A3o%20%E2%80%A2%20IA%20local&descSize=22&descAlignY=74&fontAlignY=42" alt="João Bernardes" width="100%">
</picture>

<h3><i>IA que roda na minha máquina e trabalha pra valer.</i></h3>

<a href="https://www.linkedin.com/in/joao-bernardes-478749415/"><img height="34" src="https://img.shields.io/badge/linkedin-João%20Bernardes-5C3A21?style=for-the-badge&logo=linkedin&logoColor=F5EFE6&labelColor=2B2B2B"></a>
<a href="https://github.com/exgde"><img height="34" src="https://img.shields.io/badge/github-exgde-5C3A21?style=for-the-badge&logo=github&logoColor=F5EFE6&labelColor=2B2B2B"></a>
<a href="https://joaobyss.itch.io"><img height="34" src="https://img.shields.io/badge/itch.io-joaobyss-5C3A21?style=for-the-badge&logo=itchdotio&logoColor=F5EFE6&labelColor=2B2B2B"></a>

</div>

<br>

## Sobre

Sou AI engineer em formação (Ciência da Computação, UFJ). Rodo modelos de linguagem localmente desde 2023 e hoje foco em **automação e integração inteligente**: ligar modelos a ferramentas, dados e rotinas reais.

Já passei pelas partes que quebram na prática: janela de contexto, parâmetros de inferência (temperatura, top-p, quantização), custo de GPU, e conectar tudo via **MCP (Model Context Protocol)**.

Procuro vaga júnior em AI engineering / automação. Também topo freela e colaboração.

<br>

## O que eu faço

- **IA local**: rodar e servir LLMs na minha própria GPU (hoje um Qwen3 MoE de 35B), ajustando contexto, parâmetros e quantização.
- **MCP**: criar servidores MCP que dão ferramentas e dados a agentes (Claude Code e Claude Desktop).
- **Agentes e automação**: pipelines em que o modelo decide, a ferramenta executa e uma pessoa aprova o que importa.
- **Integração**: APIs, filas, bancos (SQLite/MySQL), WhatsApp, redes sociais, agendadores.
- **Divisão de trabalho entre modelos**: o modelo local resume e rascunha de graça, o modelo grande decide e revisa.

<br>

## Stack

<p>
<img height="34" src="https://img.shields.io/badge/Claude%20Code-E8D5B7?style=for-the-badge&logo=anthropic&logoColor=5C3A21">
<img height="34" src="https://img.shields.io/badge/MCP-E8D5B7?style=for-the-badge&logoColor=5C3A21">
<img height="34" src="https://img.shields.io/badge/LLMs%20locais-E8D5B7?style=for-the-badge&logoColor=5C3A21">
<img height="34" src="https://img.shields.io/badge/Node.js-E8D5B7?style=for-the-badge&logo=nodedotjs&logoColor=5C3A21">
<img height="34" src="https://img.shields.io/badge/TypeScript-E8D5B7?style=for-the-badge&logo=typescript&logoColor=5C3A21">
<img height="34" src="https://img.shields.io/badge/Python-E8D5B7?style=for-the-badge&logo=python&logoColor=5C3A21">
</p>

<p>
<img height="34" src="https://img.shields.io/badge/SQLite-2B2B2B?style=for-the-badge&logo=sqlite&logoColor=E8D5B7">
<img height="34" src="https://img.shields.io/badge/MySQL-2B2B2B?style=for-the-badge&logo=mysql&logoColor=E8D5B7">
<img height="34" src="https://img.shields.io/badge/Docker-2B2B2B?style=for-the-badge&logo=docker&logoColor=E8D5B7">
<img height="34" src="https://img.shields.io/badge/Playwright-2B2B2B?style=for-the-badge&logo=playwright&logoColor=E8D5B7">
<img height="34" src="https://img.shields.io/badge/Remotion-2B2B2B?style=for-the-badge&logoColor=E8D5B7">
<img height="34" src="https://img.shields.io/badge/Git-2B2B2B?style=for-the-badge&logo=git&logoColor=E8D5B7">
</p>

<br>

## Projetos de IA e automação

> O código destes três ainda é privado. Estou limpando segredos e dados pessoais para abrir.

**Painel pessoal com conselho de IA**
Painel local (Node, SQLite) que reúne projetos, métricas e metas. Expõe um **servidor MCP próprio**, então o Claude lê o estado real antes de opinar. Um segundo parecer vem de um **Qwen local**, e as divergências entre os dois ficam registradas.

**Fábrica de vídeos com IA**
Pipeline que vai do roteiro ao vídeo: o Claude escreve o roteiro em JSON, a narração é gerada por IA na GPU local, a animação 3D é renderizada por código (Remotion + Three.js), uma pessoa aprova no painel e um agendador publica. Depois as métricas voltam para o Claude.

**Prospecção automatizada**
Pipeline que busca negócios locais, gera uma página de demonstração, tira o print e monta a fila de mensagens. Tem funil de status, limite diário de custo e aprovação manual antes de qualquer envio.

<br>

## Repositórios abertos

<p align="center">
<a href="https://github.com/exgde/oot-switch2-button-prompts"><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/projetos/button-prompts-dark.svg"><img src="./assets/projetos/button-prompts-light.svg" alt="Button Prompts: ícones de PlayStation, Xbox e Steam Deck no OOT (Switch 2)" width="49%"></picture></a>
<a href="https://github.com/exgde/oot-lichii-keyboard-mouse"><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/projetos/teclado-mouse-dark.svg"><img src="./assets/projetos/teclado-mouse-light.svg" alt="Teclado + Mouse: pra jogar OOT (Switch 2) no Lichii de teclado e mouse" width="49%"></picture></a>
</p>

<p align="center">
<a href="https://github.com/exgde/adega"><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/projetos/adega-dark.svg"><img src="./assets/projetos/adega-light.svg" alt="Adega: meu CrossOver caseiro, um app pra macOS que roda programas do Windows" width="49%"></picture></a>
<a href="https://github.com/exgde/biblioteca-sql"><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/projetos/biblioteca-sql-dark.svg"><img src="./assets/projetos/biblioteca-sql-light.svg" alt="Biblioteca SQL: trabalho de Banco de Dados da UFJ, modelo MySQL de uma biblioteca" width="49%"></picture></a>
</p>

<br>

## Antes disso: jogos

Faço jogos desde 2019, quase sempre de terror, em Unreal e Unity. Foi aí que aprendi a entregar coisa pronta.
Meu primeiro jogo lançado: [Goldspotting, no itch.io](https://joaobyss.itch.io/goldspotting).

<br>

<div align="center">
<h4>feito por joaobyss, com café</h4>
</div>
