const POLITICIANS = window.APP_DATA.politicians;
const TEMAS = window.APP_DATA.temas;
let currentCat = 'federal';
let selectedPolitician = null;
let selectedTema = '';

const $ = (sel) => document.querySelector(sel);
const escapeHtml = (v = '') => String(v).replace(/[&<>'"]/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
function initials(nome) {
  const parts = nome.split(' ').filter(Boolean);
  return (parts[0][0] + (parts[parts.length - 1][0] || '')).toUpperCase();
}

function renderPoliticians() {
  const query = $('#quickSearch').value.toLowerCase().trim();
  const list = (POLITICIANS[currentCat] || []).filter(p => p.nome.toLowerCase().includes(query));
  const grid = $('#politicianGrid');
  grid.innerHTML = list.length ? list.map(pol => `
    <article class="politician-card${selectedPolitician && selectedPolitician.nome === pol.nome ? ' selected' : ''}" data-nome="${escapeHtml(pol.nome)}">
      <div class="avatar">${initials(pol.nome)}</div>
      <h3>${escapeHtml(pol.nome)}</h3>
      <p>${escapeHtml(pol.cargo)} · ${escapeHtml(pol.uf)}</p>
      <div class="card-tags">${escapeHtml(pol.partido)} · desde ${escapeHtml(pol.desde)}</div>
    </article>`).join('') : '<div class="empty">Nenhum político encontrado.</div>';
  grid.querySelectorAll('.politician-card').forEach(card => {
    card.addEventListener('click', () => {
      const pol = list.find(p => p.nome === card.dataset.nome);
      if (pol) selectPolitician(pol);
    });
  });
}

function selectPolitician(pol) {
  selectedPolitician = pol;
  selectedTema = '';
  renderPoliticians();
  $('#workspace').hidden = false;
  $('#panelAvatar').textContent = initials(pol.nome);
  $('#panelName').textContent = pol.nome;
  $('#panelInfo').textContent = `${pol.cargo} · ${pol.partido} · ${pol.uf} · desde ${pol.desde}`;
  $('#customTema').value = '';
  $('#results').innerHTML = '';
  renderThemes();
  $('#workspace').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function renderThemes() {
  $('#themeList').innerHTML = TEMAS.map(t => `<button class="theme-chip${selectedTema === t ? ' active' : ''}" type="button" data-tema="${escapeHtml(t)}">${escapeHtml(t)}</button>`).join('');
  $('#themeList').querySelectorAll('.theme-chip').forEach(btn => {
    btn.addEventListener('click', () => {
      selectedTema = btn.dataset.tema;
      $('#customTema').value = '';
      renderThemes();
      buscarTema();
    });
  });
}

function buscarTema() {
  const custom = $('#customTema').value.trim();
  const tema = custom || selectedTema;
  if (!selectedPolitician || !tema) { alert('Selecione um político e um tema'); return; }
  realizarBusca(tema);
}

async function realizarBusca(tema) {
  $('#results').innerHTML = '';
  $('#loading').hidden = false;
  try {
    const res = await fetch('/api/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: tema, politician: selectedPolitician.nome })
    });
    const data = await res.json();
    renderResults(data);
  } catch (e) {
    $('#results').innerHTML = `<div class="error-box">Erro: ${escapeHtml(e.message)}</div>`;
  } finally {
    $('#loading').hidden = true;
  }
}

function statusClass(status = '') {
  const s = status.toLowerCase();
  if (s.includes('parcial')) return 'status-parcialmente';
  if (s.includes('andamento')) return 'status-andamento';
  if (s.includes('não') || s.includes('nao')) return 'status-nao';
  if (s.includes('cumprida')) return 'status-cumprida';
  return 'status-verificada';
}

function showDetail(promise) {
  const hasSource = promise.fonte_url && promise.fonte_titulo;
  const sourceHtml = hasSource
    ? `<div class="detail-source"><strong>Fonte da evidência</strong><br><a href="${escapeHtml(promise.fonte_url)}" target="_blank" rel="noreferrer">${escapeHtml(promise.fonte_titulo)} &#8599;</a><br>${escapeHtml(promise.fonte_site || '')}</div>`
    : '<div class="detail-source">Nenhuma fonte válida foi associada a esta análise.</div>';
  const panel = document.createElement('div');
  panel.className = 'detail-panel';
  panel.innerHTML = `<div class="detail-content">
      <button class="icon-button detail-close" aria-label="Fechar">&#10005;</button>
      <div class="eyebrow">${escapeHtml(promise.status || 'Não verificada')}</div>
      <h3>${escapeHtml(promise.promessa || '')}</h3>
      <p>${escapeHtml(promise.justificativa || 'A IA não encontrou contexto suficiente para explicar esta promessa.')}</p>
      ${sourceHtml}
    </div>`;
  document.body.appendChild(panel);
  panel.addEventListener('click', (e) => { if (e.target === panel || e.target.closest('.detail-close')) panel.remove(); });
}

function renderResults(data) {
  if (data.error) {
    $('#results').innerHTML = `<div class="error-box">❌ ${escapeHtml(data.error)}</div>`;
    return;
  }
  const promessas = data.promessas || [];
  if (!promessas.length) {
    $('#results').innerHTML = '<div class="empty">Nenhuma promessa encontrada para esta região/tema.</div>';
    return;
  }
  const counts = { c: 0, p: 0, n: 0, a: 0 };
  promessas.forEach(p => {
    const s = (p.status || '').toLowerCase();
    if (s.includes('parcial')) counts.p++;
    else if (s.includes('andamento')) counts.a++;
    else if (s.includes('não') || s.includes('nao')) counts.n++;
    else if (s.includes('cumprida')) counts.c++;
  });
  const sites = (data.sites_consultados || []).join(' · ');
  let html = `<div class="results-header"><h3>Promessas encontradas</h3><p>${data.total_artigos_analisados || 0} artigos analisados${sites ? ' · ' + escapeHtml(sites) : ''}</p></div>
    <div class="stats">
      <div class="stat"><strong>${counts.c}</strong><span>cumpridas</span></div>
      <div class="stat"><strong>${counts.p}</strong><span>parciais</span></div>
      <div class="stat"><strong>${counts.a}</strong><span>em andamento</span></div>
      <div class="stat"><strong>${counts.n}</strong><span>não cumpridas</span></div>
    </div>`;
  if (data.resumo_geral) html += `<div class="summary">📌 ${escapeHtml(data.resumo_geral)}</div>`;
  html += `<div class="promise-list">${promessas.map((p, i) => `
      <article class="promise-card" data-idx="${i}">
        <div class="promise-top"><h4>${escapeHtml(p.promessa || '')}</h4><span class="status ${statusClass(p.status)}">${escapeHtml(p.status || 'Indefinido')}</span></div>
        ${p.area ? `<div class="promise-area">${escapeHtml(p.area)}</div>` : ''}
        <div class="promise-hint">Clique para ler a explicação e a fonte</div>
      </article>`).join('')}</div>`;
  $('#results').innerHTML = html;
  $('#results').querySelectorAll('.promise-card').forEach(card => {
    card.addEventListener('click', () => showDetail(promessas[Number(card.dataset.idx)]));
  });
}

document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    currentCat = tab.dataset.cat;
    renderPoliticians();
  });
});
$('#quickSearch').addEventListener('input', renderPoliticians);
$('#closeWorkspace').addEventListener('click', () => { $('#workspace').hidden = true; });
$('#btnBuscar').addEventListener('click', buscarTema);
$('#customTema').addEventListener('keydown', (e) => { if (e.key === 'Enter') buscarTema(); });

renderPoliticians();
