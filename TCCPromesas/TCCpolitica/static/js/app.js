const data = window.RADAR_DATA;
let currentCategory = 'federal';
let selectedPolitician = null;
let selectedTheme = '';

const $ = (selector) => document.querySelector(selector);
const initials = (name) => name.split(' ').filter(Boolean).slice(0, 2).map((part) => part[0]).join('').toUpperCase();
const escapeHtml = (value = '') => String(value).replace(/[&<>'"]/g, (char) => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[char]));

function renderPoliticians() {
  const query = $('#politicianSearch').value.toLowerCase().trim();
  const politicians = (data.politicians[currentCategory] || []).filter((politician) => politician.nome.toLowerCase().includes(query));
  $('#politicianGrid').innerHTML = politicians.length ? politicians.map((politician) => `
    <article class="politician-card" data-id="${politician.id}">
      <div class="avatar">${initials(politician.nome)}</div>
      <h3>${escapeHtml(politician.nome)}</h3>
      <p>${escapeHtml(politician.cargo)} · ${escapeHtml(politician.uf)}</p>
      <div class="card-tags">${escapeHtml(politician.partido)} · mandato desde ${escapeHtml(politician.desde)}</div>
      ${politician.historico ? `<a class="history-link" href="/historico/${encodeURIComponent(politician.id)}" onclick="event.stopPropagation()">Ver histórico &#8599;</a>` : ''}
    </article>`).join('') : '<div class="empty">Nenhum político encontrado nesta esfera.</div>';
  document.querySelectorAll('.politician-card').forEach((card) => card.addEventListener('click', () => {
    selectedPolitician = politicians.find((politician) => politician.id === card.dataset.id);
    openWorkspace();
  }));
}

function openWorkspace() {
  $('#workspace').hidden = false;
  $('#profileAvatar').textContent = initials(selectedPolitician.nome);
  $('#profileName').textContent = selectedPolitician.nome;
  $('#profileMeta').textContent = `${selectedPolitician.cargo} · ${selectedPolitician.partido} · ${selectedPolitician.uf} · mandato desde ${selectedPolitician.desde}`;
  $('#results').innerHTML = '<div class="empty">Escolha uma categoria para verificar as promessas oficiais deste mandato.</div>';
  renderThemes();
  $('#workspace').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function renderThemes() {
  $('#themeList').innerHTML = data.themes.map((theme) => `<button class="theme-chip ${selectedTheme === theme ? 'active' : ''}" type="button">${escapeHtml(theme)}</button>`).join('');
  document.querySelectorAll('.theme-chip').forEach((button, index) => button.addEventListener('click', () => {
    selectedTheme = data.themes[index];
    renderThemes();
    searchPromises();
  }));
}

function statusClass(status = '') {
  const normalized = status.toLowerCase();
  if (normalized.includes('parcial')) return 'status-parcialmente';
  if (normalized.includes('cumprida')) return 'status-cumprida';
  if (normalized.includes('andamento')) return 'status-andamento';
  if (normalized.includes('nao') || normalized.includes('não')) return 'status-nao';
  return 'status-verificada';
}

function showPromiseDetail(promise) {
  const source = promise.fonte || {};
  const sourceHtml = source.url ? `<div class="detail-source"><strong>Fonte da evidência</strong><br><a href="${escapeHtml(source.url)}" target="_blank" rel="noreferrer">${escapeHtml(source.title)} &#8599;</a><br>${escapeHtml(source.site)}</div>` : '<div class="detail-source">Nenhuma fonte válida foi associada a esta análise.</div>';
  const panel = document.createElement('div');
  panel.className = 'detail-panel';
  panel.innerHTML = `<div class="detail-content"><button class="icon-button detail-close" aria-label="Fechar">&#10005;</button><div class="eyebrow">${escapeHtml(promise.status || 'Não verificada')}</div><h3>${escapeHtml(promise.promessa)}</h3><p>${escapeHtml(promise.explicacao || promise.justificativa || 'A IA não encontrou contexto suficiente para explicar esta promessa.')}</p>${sourceHtml}</div>`;
  document.body.appendChild(panel);
  panel.addEventListener('click', (event) => { if (event.target === panel || event.target.closest('.detail-close')) panel.remove(); });
}

function renderResults(result) {
  if (result.error) { $('#results').innerHTML = `<div class="notice">${escapeHtml(result.error)}</div>`; return; }
  const promises = result.promessas || [];
  if (!promises.length) { $('#results').innerHTML = '<div class="empty">Nenhuma promessa encontrada para esta área.</div>'; return; }
  const counts = { cumprida: 0, parcial: 0, andamento: 0, nao: 0 };
  promises.forEach((promise) => { const status = (promise.status || '').toLowerCase(); if (status.includes('parcial')) counts.parcial++; else if (status.includes('andamento')) counts.andamento++; else if (status.includes('nao') || status.includes('não')) counts.nao++; else if (status.includes('cumprida')) counts.cumprida++; });
  $('#results').innerHTML = `<div class="results-header"><h3>Promessas encontradas</h3><p>${result.total_artigos_analisados || 0} notícias analisadas</p></div><div class="stats"><div class="stat"><strong>${counts.cumprida}</strong><span>cumpridas</span></div><div class="stat"><strong>${counts.parcial}</strong><span>parciais</span></div><div class="stat"><strong>${counts.andamento}</strong><span>em andamento</span></div><div class="stat"><strong>${counts.nao}</strong><span>não cumpridas</span></div></div>${result.resumo_geral ? `<div class="summary">${escapeHtml(result.resumo_geral)}</div>` : ''}<div class="promise-list">${promises.map((promise, index) => `<article class="promise-card" data-promise="${index}"><div class="promise-top"><h4>${escapeHtml(promise.promessa)}</h4><span class="status ${statusClass(promise.status)}">${escapeHtml(promise.status || 'Não verificada')}</span></div><div class="promise-area">${escapeHtml(promise.area || selectedTheme)}</div><div class="promise-hint">Clique para ler a explicação e a fonte</div></article>`).join('')}</div>`;
  document.querySelectorAll('.promise-card').forEach((card) => card.addEventListener('click', () => showPromiseDetail(promises[Number(card.dataset.promise)])));
}

async function searchPromises() {
  const theme = selectedTheme;
  if (!selectedPolitician || !theme) return;
  $('#loading').hidden = false;
  $('#results').innerHTML = '';
  try {
    const response = await fetch('/api/search', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ politician: selectedPolitician.nome, query: theme }) });
    renderResults(await response.json());
  } catch (error) { $('#results').innerHTML = `<div class="notice">Não foi possível concluir a busca: ${escapeHtml(error.message)}</div>`; }
  finally { $('#loading').hidden = true; }
}

document.querySelectorAll('.tab').forEach((tab) => tab.addEventListener('click', () => { document.querySelectorAll('.tab').forEach((item) => item.classList.remove('active')); tab.classList.add('active'); currentCategory = tab.dataset.category; renderPoliticians(); }));
$('#politicianSearch').addEventListener('input', renderPoliticians);
$('#closeWorkspace').addEventListener('click', () => { $('#workspace').hidden = true; });
$('#syncButton').addEventListener('click', async () => {
  const button = $('#syncButton');
  button.disabled = true;
  button.textContent = 'Atualizando...';
  try {
    const response = await fetch('/api/sync', { method: 'POST' });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Falha ao sincronizar');
    alert(`${result.perfis_importados} perfis atualizados. ${result.promessas_verificadas} promessas verificadas.`);
  } catch (error) { alert(error.message); }
  finally { button.disabled = false; button.textContent = 'Atualizar Notícias'; }
});
renderPoliticians();
