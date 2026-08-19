import os, re, json
from flask import Flask, render_template_string, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9",
}

POLITICIANS = {
    "federal": [
        {"nome": "Luiz Inácio Lula da Silva", "cargo": "Presidente da República",    "partido": "PT",           "uf": "BR", "desde": "2023"},
        {"nome": "Geraldo Alckmin",            "cargo": "Vice-Presidente",            "partido": "PSB",          "uf": "BR", "desde": "2023"},
        {"nome": "Rodrigo Pacheco",            "cargo": "Presidente do Senado",       "partido": "PSD",          "uf": "MG", "desde": "2021"},
        {"nome": "Arthur Lira",                "cargo": "Presidente da Câmara",       "partido": "PP",           "uf": "AL", "desde": "2021"},
        {"nome": "Fernando Haddad",            "cargo": "Min. Fazenda",               "partido": "PT",           "uf": "SP", "desde": "2023"},
        {"nome": "Flávio Dino",                "cargo": "Min. STF / ex-Min. Justiça", "partido": "PSB",          "uf": "MA", "desde": "2023"},
        {"nome": "Simone Tebet",               "cargo": "Min. Planejamento",          "partido": "MDB",          "uf": "MS", "desde": "2023"},
        {"nome": "Alexandre Silveira",         "cargo": "Min. Minas e Energia",       "partido": "PSD",          "uf": "MG", "desde": "2023"},
    ],
    "governadores": [
        {"nome": "Gladson Cameli",      "cargo": "Governador", "partido": "PP",            "uf": "AC", "desde": "2019"},
        {"nome": "Paulo Dantas",        "cargo": "Governador", "partido": "MDB",           "uf": "AL", "desde": "2022"},
        {"nome": "Wilson Lima",         "cargo": "Governador", "partido": "União Brasil",  "uf": "AM", "desde": "2019"},
        {"nome": "Clécio Luís",         "cargo": "Governador", "partido": "Solidariedade", "uf": "AP", "desde": "2023"},
        {"nome": "Jerônimo Rodrigues",  "cargo": "Governador", "partido": "PT",            "uf": "BA", "desde": "2023"},
        {"nome": "Elmano de Freitas",   "cargo": "Governador", "partido": "PT",            "uf": "CE", "desde": "2023"},
        {"nome": "Ibaneis Rocha",       "cargo": "Governador", "partido": "MDB",           "uf": "DF", "desde": "2019"},
        {"nome": "Renato Casagrande",   "cargo": "Governador", "partido": "PSB",           "uf": "ES", "desde": "2019"},
        {"nome": "Ronaldo Caiado",      "cargo": "Governador", "partido": "União Brasil",  "uf": "GO", "desde": "2019"},
        {"nome": "Carlos Brandão",      "cargo": "Governador", "partido": "PSB",           "uf": "MA", "desde": "2023"},
        {"nome": "Romeu Zema",          "cargo": "Governador", "partido": "Novo",          "uf": "MG", "desde": "2019"},
        {"nome": "Eduardo Riedel",      "cargo": "Governador", "partido": "PSDB",          "uf": "MS", "desde": "2023"},
        {"nome": "Mauro Mendes",        "cargo": "Governador", "partido": "União Brasil",  "uf": "MT", "desde": "2019"},
        {"nome": "Helder Barbalho",     "cargo": "Governador", "partido": "MDB",           "uf": "PA", "desde": "2019"},
        {"nome": "João Azevêdo",        "cargo": "Governador", "partido": "PSB",           "uf": "PB", "desde": "2019"},
        {"nome": "Raquel Lyra",         "cargo": "Governadora","partido": "PSDB",          "uf": "PE", "desde": "2023"},
        {"nome": "Rafael Fonteles",     "cargo": "Governador", "partido": "PT",            "uf": "PI", "desde": "2023"},
        {"nome": "Ratinho Junior",      "cargo": "Governador", "partido": "PSD",           "uf": "PR", "desde": "2019"},
        {"nome": "Cláudio Castro",      "cargo": "Governador", "partido": "PL",            "uf": "RJ", "desde": "2021"},
        {"nome": "Fátima Bezerra",      "cargo": "Governadora","partido": "PT",            "uf": "RN", "desde": "2019"},
        {"nome": "Marcos Rocha",        "cargo": "Governador", "partido": "União Brasil",  "uf": "RO", "desde": "2019"},
        {"nome": "Arthur Henrique",     "cargo": "Governador", "partido": "MDB",           "uf": "RR", "desde": "2023"},
        {"nome": "Eduardo Leite",       "cargo": "Governador", "partido": "PSDB",          "uf": "RS", "desde": "2019"},
        {"nome": "Jorginho Mello",      "cargo": "Governador", "partido": "PL",            "uf": "SC", "desde": "2023"},
        {"nome": "Fábio Mitidieri",     "cargo": "Governador", "partido": "PSD",           "uf": "SE", "desde": "2023"},
        {"nome": "Tarcísio de Freitas", "cargo": "Governador", "partido": "Republicanos",  "uf": "SP", "desde": "2023"},
        {"nome": "Wanderlei Barbosa",   "cargo": "Governador", "partido": "Republicanos",  "uf": "TO", "desde": "2022"},
    ],
    "prefeitos": [
        {"nome": "Ricardo Nunes",    "cargo": "Prefeito",  "partido": "MDB",          "uf": "SP",  "desde": "2021"},
        {"nome": "Eduardo Paes",     "cargo": "Prefeito",  "partido": "PSD",          "uf": "RJ",  "desde": "2021"},
        {"nome": "Fuad Noman",       "cargo": "Prefeito",  "partido": "PSD",          "uf": "BH",  "desde": "2024"},
        {"nome": "David Almeida",    "cargo": "Prefeito",  "partido": "Avante",       "uf": "AM",  "desde": "2021"},
        {"nome": "Igor Normando",    "cargo": "Prefeito",  "partido": "MDB",          "uf": "PA",  "desde": "2025"},
        {"nome": "Bruno Reis",       "cargo": "Prefeito",  "partido": "União Brasil", "uf": "BA",  "desde": "2021"},
        {"nome": "Evandro Leitão",   "cargo": "Prefeito",  "partido": "PT",           "uf": "CE",  "desde": "2025"},
        {"nome": "João Campos",      "cargo": "Prefeito",  "partido": "PSB",          "uf": "PE",  "desde": "2021"},
        {"nome": "Sebastião Melo",   "cargo": "Prefeito",  "partido": "MDB",          "uf": "RS",  "desde": "2021"},
        {"nome": "Eduardo Pimentel", "cargo": "Prefeito",  "partido": "PSD",          "uf": "PR",  "desde": "2025"},
        {"nome": "Sandro Mabel",     "cargo": "Prefeito",  "partido": "União Brasil", "uf": "GO",  "desde": "2025"},
        {"nome": "Leandro Grass",    "cargo": "Prefeito",  "partido": "PV",           "uf": "DF",  "desde": "2025"},
    ],
}

TEMAS_PROMESSAS = [
    "saúde pública", "educação", "segurança pública",
    "geração de empregos", "infraestrutura", "meio ambiente",
    "reforma tributária", "habitação e moradia",
    "combate à corrupção", "transporte e mobilidade",
    "assistência social", "desenvolvimento econômico",
]

SITES = [
    {
        "nome": "UOL",
        "url": "https://busca.uol.com.br/result.htm?q={query}&site=noticias.uol.com.br",
        "seletores": ["li.result", "div.result-item", "article"],
    },
    {
        "nome": "G1 Globo",
        "url": "https://g1.globo.com/busca/?q={query}&species=noticia",
        "seletores": ["div.widget--info", "div.feed-post-body", "li.widget--card"],
    },
    {
        "nome": "R7",
        "url": "https://buscar.r7.com/buscar?q={query}",
        "seletores": ["div.card-noticia", "article"],
    },
    {
        "nome": "Agência Brasil",
        "url": "https://agenciabrasil.ebc.com.br/busca/node?keys={query}",
        "seletores": ["div.views-row", "article"],
    },

    {
        "nome": "Estadão",
        "url": "https://busca.estadao.com.br/?q={query}",
        "seletores": ["div.search-results-item", "div.news-item", "article"],
    },
    {
        "nome": "Terra",
        "url": "https://www.terra.com.br/busca/?q={query}",
        "seletores": ["div.result-item", "article", "div.card"],
    },
    {
        "nome": "Band",
        "url": "https://www.band.uol.com.br/busca?q={query}",
        "seletores": ["div.search-result", "article", "div.noticia"],
    },
    {
        "nome": "Metrópoles",
        "url": "https://www.metropoles.com/busca?q={query}",
        "seletores": ["div.search-result-item", "article", "div.card"],
    },
    {
        "nome": "Correio Braziliense",
        "url": "https://www.correiobraziliense.com.br/busca?q={query}",
        "seletores": ["div.busca-resultado", "article", "div.card"],
    },
]

def scrape_google_news(query: str, max_results: int = 10) -> list[dict]:
    """Fonte principal: RSS de busca do Google Notícias. Agrega centenas de
    veículos brasileiros reais (G1, Folha, Estadão, CNN, Metrópoles, etc) em
    um formato estruturado (XML) que não quebra a cada redesign de site,
    diferente do scraping direto de HTML de cada portal."""
    results = []
    url = f"https://news.google.com/rss/search?q={requests.utils.quote(query)}&hl=pt-BR&gl=BR&ceid=BR:pt-BR"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, "xml")
        for item in soup.find_all("item")[:max_results]:
            title_el  = item.find("title")
            link_el   = item.find("link")
            desc_el   = item.find("description")
            source_el = item.find("source")
            title = title_el.get_text(strip=True) if title_el else ""
            link  = link_el.get_text(strip=True) if link_el else ""
            desc_raw = desc_el.get_text(strip=True) if desc_el else ""
            desc  = BeautifulSoup(desc_raw, "html.parser").get_text(strip=True)[:300]
            site  = source_el.get_text(strip=True) if source_el else "Google Notícias"
            if title and link:
                results.append({"title": title, "url": link, "summary": desc, "site": site})
    except Exception as e:
        print(f"  [Google Notícias] erro: {e}")
    return results

def scrape_site(site: dict, query: str, max_results: int = 4) -> list[dict]:
    results = []
    url = site["url"].format(query=requests.utils.quote(query))
    try:
        resp = requests.get(url, headers=HEADERS, timeout=8)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        items = []
        for sel in site["seletores"]:
            items = soup.select(sel)
            if items:
                break
        if not items:
            items = soup.find_all(
                ["article", "li", "div"],
                class_=re.compile(r"result|noticia|card|news|item", re.I)
            )
        for item in items[:max_results]:
            a_tag    = item.find("a", href=True)
            title_el = item.find(["h2", "h3", "h4", "strong"])
            desc_el  = item.find(["p", "span"], class_=re.compile(r"desc|summ|text|lead", re.I))
            title = (title_el.get_text(strip=True) if title_el
                     else (a_tag.get_text(strip=True) if a_tag else ""))
            href  = a_tag["href"] if a_tag else ""
            if href and not href.startswith("http"):
                href = "https://" + href.lstrip("/")
            desc  = desc_el.get_text(strip=True)[:300] if desc_el else ""
            if title and len(title) > 20:
                results.append({"title": title, "url": href, "summary": desc, "site": site["nome"]})
    except Exception as e:
        print(f"  [{site['nome']}] erro: {e}")
    return results

def scrape_all(query: str, max_per_site: int = 4) -> list[dict]:
    all_articles = []

    gn_articles = scrape_google_news(query, max_results=10)
    all_articles.extend(gn_articles)
    if gn_articles:
        print(f"  [Google Notícias] {len(gn_articles)} artigos")

    for site in SITES:
        arts = scrape_site(site, query, max_per_site)
        all_articles.extend(arts)
        if arts:
            print(f"  [{site['nome']}] {len(arts)} artigos")

    seen, unique = set(), []
    for a in all_articles:
        if a["url"] not in seen and a["title"]:
            seen.add(a["url"])
            unique.append(a)
    return unique

HTML = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Promessas Políticas</title>
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600&family=Playfair+Display:wght@700&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Sora',sans-serif;background:#f5f4f0;color:#1a1a18;min-height:100vh}
.page{max-width:960px;margin:0 auto;padding:2rem 1.25rem}
.hero{text-align:center;padding:2.5rem 0 2rem}
.badge{display:inline-block;font-size:11px;letter-spacing:.07em;text-transform:uppercase;color:#185FA5;background:#E6F1FB;border:1px solid #B5D4F4;padding:4px 14px;border-radius:999px;margin-bottom:1.1rem}
.hero h1{font-family:'Playfair Display',serif;font-size:2.5rem;line-height:1.15;margin-bottom:.6rem}
.hero h1 span{color:#185FA5}
.hero p{font-size:.9rem;color:#5F5E5A;max-width:500px;margin:0 auto}
.tabs{display:flex;gap:6px;margin:1.5rem 0 1rem;flex-wrap:wrap}
.tab{padding:8px 20px;border-radius:999px;font-size:13px;font-weight:500;cursor:pointer;border:1px solid #D3D1C7;background:#fff;color:#5F5E5A}
.tab.active,.tab:hover{background:#185FA5;color:#fff;border-color:#185FA5}
.search-bar{display:flex;gap:8px;margin-bottom:1.25rem}
.search-bar input{flex:1;padding:10px 14px;border:1px solid #D3D1C7;border-radius:8px;background:#fff;font-size:14px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(175px,1fr));gap:10px;margin-bottom:2rem}
.pol-card{background:#fff;border:1px solid #D3D1C7;border-radius:12px;padding:1rem;cursor:pointer;text-align:center}
.pol-card.selected{border-color:#185FA5;background:#E6F1FB}
.pol-avatar{width:50px;height:50px;border-radius:50%;margin:0 auto .6rem;display:flex;align-items:center;justify-content:center;font-weight:600;color:#fff}
.av-f{background:#185FA5}.av-g{background:#3B6D11}.av-p{background:#854F0B}
.pol-name{font-size:13px;font-weight:500}
.pol-cargo{font-size:11px;color:#888780}
.tag{font-size:10px;padding:2px 7px;border-radius:4px;background:#F1EFE8;color:#5F5E5A;margin:3px;display:inline-block}
.promise-panel{background:#fff;border:2px solid #185FA5;border-radius:14px;padding:1.5rem;margin-bottom:1.5rem}
.tema-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(138px,1fr));gap:7px;margin-bottom:1rem}
.tema-btn{padding:8px 10px;border:1px solid #D3D1C7;border-radius:8px;background:#f9f8f5;font-size:12px;cursor:pointer}
.tema-btn.selected{border-color:#185FA5;background:#185FA5;color:#fff}
.custom-row{display:flex;gap:8px}
.custom-row input{flex:1;padding:9px 12px;border:1px solid #D3D1C7;border-radius:8px}
.btn{padding:9px 20px;background:#185FA5;color:#fff;border:none;border-radius:8px;cursor:pointer}
.btn:disabled{background:#B5D4F4}
.status-bar{background:#E6F1FB;border:1px solid #B5D4F4;border-radius:8px;padding:.875rem 1.25rem;margin:1rem 0;display:flex;align-items:center;gap:10px}
.spinner{width:15px;height:15px;border:2px solid #B5D4F4;border-top-color:#185FA5;border-radius:50%;animation:spin .7s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.stats-row{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:1.25rem}
.stat{background:#fff;border:1px solid #D3D1C7;border-radius:10px;padding:.875rem;text-align:center}
.stat-n{font-size:22px;font-weight:600}
.stat-l{font-size:11px;color:#888780}
.s-c .stat-n{color:#3B6D11}.s-p .stat-n{color:#BA7517}.s-n .stat-n{color:#E24B4A}.s-a .stat-n{color:#185FA5}
.resumo-box{background:#E6F1FB;border-radius:8px;padding:1rem;font-size:13px;margin-bottom:1rem}
.sites-box{font-size:11px;color:#888780;margin-bottom:.875rem}
.card{background:#fff;border:1px solid #D3D1C7;border-radius:12px;padding:1.25rem;margin-bottom:.75rem}
.card-top{display:flex;align-items:flex-start;gap:12px}
.dot{width:10px;height:10px;border-radius:50%;flex-shrink:0;margin-top:5px}
.d-c{background:#639922}.d-p{background:#BA7517}.d-n{background:#E24B4A}.d-a{background:#185FA5}.d-i{background:#888780}
.card-promise{flex:1;font-size:.875rem;font-weight:500}
.badge2{font-size:11px;padding:3px 10px;border-radius:999px;white-space:nowrap}
.b-c{background:#EAF3DE;color:#3B6D11}.b-p{background:#FAEEDA;color:#854F0B}.b-n{background:#FCEBEB;color:#A32D2D}.b-a{background:#E6F1FB;color:#185FA5}
.card-area{font-size:11px;padding:2px 8px;background:#F1EFE8;border-radius:4px;display:inline-block;margin:.5rem 0}
.card-analysis{font-size:12px;color:#5F5E5A;border-left:3px solid #D3D1C7;padding-left:.75rem}
.card-source{font-size:11px;margin-top:.6rem}
.card-source a{color:#185FA5}
.footer{text-align:center;padding:2rem 0 1rem;font-size:11px;color:#B4B2A9}
.error-box{background:#FCEBEB;border:1px solid #F09595;border-radius:8px;padding:1rem;color:#A32D2D}
@media(max-width:600px){.stats-row{grid-template-columns:repeat(2,1fr)}.hero h1{font-size:1.8rem}}
</style>
</head>
<body>
<div class="page">
  <div class="hero">
    <div class="badge">TCC · ETEC Camargo Aranha · 2026</div>
    <h1>Promessas <span>Políticas</span></h1>
    <p>Escolha um político e um tema para ver se as promessas foram cumpridas</p>
  </div>

  {% if not api_key %}
  <div class="error-box">⚠ <strong>GROQ_API_KEY não encontrada.</strong> Configure e reinicie.</div>
  {% endif %}

  <div class="tabs">
    <div class="tab active" onclick="showTab('federal',this)">🇧🇷 Federal</div>
    <div class="tab" onclick="showTab('governadores',this)">🏛 Governadores</div>
    <div class="tab" onclick="showTab('prefeitos',this)">🏙 Prefeitos</div>
  </div>

  <div class="search-bar">
    <input type="text" id="quickSearch" placeholder="🔎 Filtrar político por nome">
  </div>

  <div id="tab-federal"><div class="grid" id="grid-federal"></div></div>
  <div id="tab-governadores" style="display:none"><div class="grid" id="grid-governadores"></div></div>
  <div id="tab-prefeitos" style="display:none"><div class="grid" id="grid-prefeitos"></div></div>

  <div id="promisePanel" style="display:none" class="promise-panel">
    <div class="panel-header" style="display:flex; gap:14px; align-items:center; margin-bottom:1rem">
      <div id="panelAvatar" class="panel-avatar"></div>
      <div><h2 id="panelName"></h2><p id="panelInfo" style="font-size:12px; color:#888"></p></div>
    </div>
    <p class="temas-label">Ou escolha um tema:</p>
    <div class="tema-grid" id="temaGrid"></div>
    <div class="custom-row">
      <input type="text" id="customTema" placeholder="Ou digite um tema específico">
      <button class="btn" onclick="buscarTema()">Buscar</button>
    </div>
  </div>

  <div id="statusBar" style="display:none" class="status-bar">
    <div class="spinner"></div>
    <span id="statusText">Coletando notícias...</span>
  </div>

  <div id="results"></div>

  <div class="footer">
    Felipe Gusmão · Aquiles Menezes · Heitor Ribeiro · Artur Araujo · Andre Garrido<br>
    Fontes: UOL · G1 · Estadão · Terra · Band · Metrópoles · R7 · Agência Brasil · Correio Braziliense<br>
    IA: Groq Llama 3.3 (gratuito)
  </div>
</div>

<script>
const POLITICIANS = {{ politicians_json|safe }};
const TEMAS = {{ temas_json|safe }};
let selectedPolitician = null;
let selectedTema = null;
let currentCat = 'federal';

function initGrids() {
  for (let cat of ['federal','governadores','prefeitos']) {
    const grid = document.getElementById('grid-'+cat);
    const avCls = cat==='federal'?'av-f':cat==='governadores'?'av-g':'av-p';
    POLITICIANS[cat].forEach(pol => {
      const parts = pol.nome.split(' ');
      const initials = (parts[0][0] + (parts[parts.length-1][0]||'')).toUpperCase();
      const div = document.createElement('div');
      div.className = 'pol-card';
      div.dataset.nome = pol.nome.toLowerCase();
      div.innerHTML = `
        <div class="pol-avatar ${avCls}">${initials}</div>
        <div class="pol-name">${pol.nome}</div>
        <div class="pol-cargo">${pol.cargo}</div>
        <div class="pol-meta"><span class="tag">${pol.partido}</span><span class="tag">${pol.uf}</span><span class="tag">desde ${pol.desde}</span></div>`;
      div.onclick = () => selectPolitician(pol, cat, div);
      grid.appendChild(div);
    });
  }
}

function showTab(tab, el) {
  ['federal','governadores','prefeitos'].forEach(t => {
    document.getElementById('tab-'+t).style.display = t===tab?'block':'none';
  });
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  el.classList.add('active');
  currentCat = tab;
}

function selectPolitician(pol, cat, cardEl) {
  selectedPolitician = pol;
  document.querySelectorAll('.pol-card').forEach(c => c.classList.remove('selected'));
  cardEl.classList.add('selected');
  const parts = pol.nome.split(' ');
  const initials = (parts[0][0] + (parts[parts.length-1][0]||'')).toUpperCase();
  const avCls = cat==='federal'?'av-f':cat==='governadores'?'av-g':'av-p';
  document.getElementById('panelAvatar').textContent = initials;
  document.getElementById('panelAvatar').className = 'panel-avatar ' + avCls;
  document.getElementById('panelName').textContent = pol.nome;
  document.getElementById('panelInfo').textContent = `${pol.cargo} · ${pol.partido} · ${pol.uf} · desde ${pol.desde}`;
  const grid = document.getElementById('temaGrid');
  grid.innerHTML = '';
  TEMAS.forEach(tema => {
    const btn = document.createElement('button');
    btn.className = 'tema-btn';
    btn.textContent = tema;
    btn.onclick = () => {
      document.querySelectorAll('.tema-btn').forEach(b => b.classList.remove('selected'));
      btn.classList.add('selected');
      selectedTema = tema;
      document.getElementById('customTema').value = '';
      buscarTema();
    };
    grid.appendChild(btn);
  });
  document.getElementById('customTema').value = '';
  document.getElementById('promisePanel').style.display = 'block';
  document.getElementById('results').innerHTML = '';
  document.getElementById('promisePanel').scrollIntoView({behavior:'smooth'});
}

async function buscarTema() {
  const custom = document.getElementById('customTema').value.trim();
  const tema = custom || selectedTema;
  if (!tema || !selectedPolitician) return alert('Selecione um político e um tema');
  await realizarBusca(selectedPolitician.nome, tema);
}

async function realizarBusca(politicianName, tema) {
  document.getElementById('results').innerHTML = '';
  document.getElementById('statusBar').style.display = 'flex';
  document.getElementById('statusText').innerText = 'Raspando notícias...';
  try {
    const res = await fetch('/api/search', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({query: tema, politician: politicianName})
    });
    const data = await res.json();
    document.getElementById('statusBar').style.display = 'none';
    renderResults(data);
  } catch(e) {
    document.getElementById('statusBar').style.display = 'none';
    document.getElementById('results').innerHTML = `<div class="error-box">Erro: ${e.message}</div>`;
  }
}

function renderResults(data) {
  if (data.error) {
    document.getElementById('results').innerHTML = `<div class="error-box">❌ ${data.error}</div>`;
    return;
  }
  const promessas = data.promessas || [];
  if (!promessas.length) {
    document.getElementById('results').innerHTML = '<div class="empty">Nenhuma promessa encontrada para esta região/tema.</div>';
    return;
  }
  const counts = {c:0,p:0,n:0,a:0};
  promessas.forEach(p => {
    const s = (p.status || '').toLowerCase();
    if (s.includes('parcial')) counts.p++;
    else if (s.includes('andamento')) counts.a++;
    else if (s.includes('não') || s.includes('nao')) counts.n++;
    else if (s.includes('cumprida')) counts.c++;
  });
  const sites = (data.sites_consultados || []).join(' · ');
  let html = `<div class="sites-box">📰 ${data.total_artigos_analisados || 0} artigos de: ${sites}</div>
    <div class="stats-row">
      <div class="stat s-c"><div class="stat-n">${counts.c}</div><div class="stat-l">Cumpridas</div></div>
      <div class="stat s-p"><div class="stat-n">${counts.p}</div><div class="stat-l">Parcialmente</div></div>
      <div class="stat s-n"><div class="stat-n">${counts.n}</div><div class="stat-l">Não cumpridas</div></div>
      <div class="stat s-a"><div class="stat-n">${counts.a}</div><div class="stat-l">Em andamento</div></div>
    </div>`;
  if (data.resumo_geral) html += `<div class="resumo-box">📌 ${data.resumo_geral}</div>`;
  promessas.forEach(p => {
    const s = (p.status || '').toLowerCase();
    let statusClass = 'i', badgeClass = 'b-i', dotClass = 'd-i';
    if (s.includes('parcial')) { statusClass='p'; badgeClass='b-p'; dotClass='d-p'; }
    else if (s.includes('andamento')) { statusClass='a'; badgeClass='b-a'; dotClass='d-a'; }
    else if (s.includes('não')) { statusClass='n'; badgeClass='b-n'; dotClass='d-n'; }
    else if (s.includes('cumprida')) { statusClass='c'; badgeClass='b-c'; dotClass='d-c'; }
    html += `<div class="card">
      <div class="card-top">
        <div class="dot ${dotClass}"></div>
        <div class="card-promise">${p.promessa || ''}</div>
        <span class="badge2 ${badgeClass}">${p.status || 'Indefinido'}</span>
      </div>
      ${p.area ? `<div class="card-area">🏷 ${p.area}</div>` : ''}
      <div class="card-analysis">${p.justificativa || ''}</div>
      ${p.fonte_titulo ? `<div class="card-source">Fonte (${p.fonte_site || ''}): <a href="${p.fonte_url}" target="_blank">${p.fonte_titulo}</a></div>` : ''}
    </div>`;
  });
  document.getElementById('results').innerHTML = html;
}

document.addEventListener('DOMContentLoaded', () => {
  initGrids();
  document.getElementById('quickSearch').addEventListener('input', function(e) {
    const q = e.target.value.toLowerCase();
    document.querySelectorAll('.pol-card').forEach(c => {
      c.style.display = (!q || c.dataset.nome.includes(q)) ? '' : 'none';
    });
  });
});
</script>
</body>
</html>"""

@app.route("/")
def index():
    return render_template_string(
        HTML,
        api_key=bool(GROQ_API_KEY),
        politicians_json=json.dumps(POLITICIANS, ensure_ascii=False),
        temas_json=json.dumps(TEMAS_PROMESSAS, ensure_ascii=False),
    )

@app.route("/api/search", methods=["POST"])
def api_search():
    body = request.get_json(force=True)
    query = body.get("query", "").strip()
    politician = body.get("politician", "").strip()
    if not query:
        return jsonify({"error": "Parâmetro query obrigatório"}), 400
    if not GROQ_API_KEY:
        return jsonify({"error": "GROQ_API_KEY não configurada"}), 500

    search_query = f"{politician} promessa {query}"
    articles = scrape_all(search_query)
    result = filter_with_ai(articles, query, politician)
    return jsonify(result)

def filter_with_ai(articles: list[dict], tema: str, politician: str) -> dict:
    if not GROQ_API_KEY:
        return {"error": "GROQ_API_KEY não configurada"}
    if not articles:
        return {"error": "Nenhum artigo foi encontrado para essa busca. Tente outro tema."}

    artigos_usados = articles[:12]
    contexto = "\n\n".join(
        f"[ARTIGO {i}] Site: {a['site']}\nTítulo: {a['title']}\nResumo: {a['summary']}"
        for i, a in enumerate(artigos_usados)
    )
    prompt = f"""Você é um verificador de promessas políticas. Analise SOMENTE os artigos abaixo sobre {politician} e o tema "{tema}".

{contexto}

REGRAS OBRIGATÓRIAS:
- Toda promessa que você reportar precisa estar EXPLICITAMENTE mencionada em pelo menos um dos artigos acima. Não invente promessas, datas, números ou declarações que não estejam no texto dos artigos.
- Para cada promessa, informe o campo "fonte_artigo_id" com o número [ARTIGO N] de onde você tirou a informação (apenas o número inteiro N). Não invente esse número, use somente os que existem acima.
- Se os artigos não derem informação suficiente para avaliar o cumprimento, use status "não verificada" mesmo assim, mas ainda cite o fonte_artigo_id do artigo que menciona a promessa.
- Se nenhum artigo mencionar nenhuma promessa relevante ao tema, retorne "promessas": [].

Retorne APENAS um JSON válido, sem texto antes ou depois, no formato:
{{"promessas": [{{"promessa": "...", "status": "cumprida|parcialmente cumprida|não cumprida|em andamento|não verificada", "justificativa": "...", "fonte_artigo_id": 0}}], "resumo_geral": "..."}}"""
    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={"model": "openai/gpt-oss-120b", "messages": [{"role": "user", "content": prompt}], "max_tokens": 2500, "temperature": 0.2},
            timeout=40,
        )
        data = resp.json()

        if not resp.ok or "choices" not in data:
            msg = data.get("error", {}).get("message", json.dumps(data, ensure_ascii=False))
            return {"error": f"Groq API ({resp.status_code}): {msg}"}

        raw = data["choices"][0]["message"]["content"]
        raw = re.sub(r"```json|```", "", raw).strip()
        m = re.search(r"\{[\s\S]*\}", raw)
        if not m:
            return {"error": "JSON não encontrado na resposta da IA"}
        parsed = json.loads(m.group())
        promessas_validadas = []
        for p in parsed.get("promessas", []):
            fid = p.get("fonte_artigo_id")
            artigo = None
            if isinstance(fid, int) and 0 <= fid < len(artigos_usados):
                artigo = artigos_usados[fid]
            if artigo and artigo.get("url"):
                p["fonte_titulo"] = artigo["title"]
                p["fonte_site"] = artigo["site"]
                p["fonte_url"] = artigo["url"]
            else:
                p["fonte_titulo"] = ""
                p["fonte_site"] = ""
                p["fonte_url"] = ""
                if "verificad" not in (p.get("status") or "").lower():
                    p["status"] = "não verificada"
            p.pop("fonte_artigo_id", None)
            promessas_validadas.append(p)
        parsed["promessas"] = promessas_validadas
        return parsed
    except requests.exceptions.RequestException as e:
        return {"error": f"Falha de conexão com a Groq: {e}"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    total_pols = sum(len(v) for v in POLITICIANS.values())
    print("\n" + "="*55)
    print("  RASTREADOR DE PROMESSAS POLÍTICAS")
    print("  TCC · ETEC Camargo Aranha · 2026")
    print("="*55)
    if not GROQ_API_KEY:
        print("\n  ⚠  GROQ_API_KEY não encontrada! Crie uma chave grátis em console.groq.com")
    print(f"\n  {total_pols} políticos cadastrados | {len(SITES)} sites de notícias")
    print("  Acesse: http://localhost:5000\n" + "="*55)
    app.run(debug=True, port=5000)