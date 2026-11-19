const POLITICIANS = window.APP_DATA.politicians;
let currentCat = 'federal';
let selectedPolitician = null;
let requestToken = 0;       // descarta respostas de político que não está mais selecionado
let statusFilter = 'todos';
let lastData = null;
const manutencaoTentada = new Set();   // evita repetir a manutenção do mesmo político na mesma sessão

const $ = (sel) => document.querySelector(sel);

// =============================== IMAGENS ===============================
const CAPITAIS = {AC:'Rio Branco',AL:'Maceió',AP:'Macapá',AM:'Manaus',BA:'Salvador',CE:'Fortaleza',DF:'Brasília',ES:'Vitória',
  GO:'Goiânia',MA:'São Luís',MT:'Cuiabá',MS:'Campo Grande',MG:'Belo Horizonte',PA:'Belém',PB:'João Pessoa',PR:'Curitiba',
  PE:'Recife',PI:'Teresina',RJ:'Rio de Janeiro',RN:'Natal',RS:'Porto Alegre',RO:'Porto Velho',RR:'Boa Vista',SC:'Florianópolis',
  SP:'São Paulo',SE:'Aracaju',TO:'Palmas'};

function cidadeDoPolitico(pol) {
  if (/^prefeit/i.test(pol.cargo) && pol.cargo.includes(' - ')) return pol.cargo.split(' - ')[1].trim();
  if (/^governador/i.test(pol.cargo)) return CAPITAIS[pol.uf] || 'Brasília';
  return 'Brasília';
}

// --- busca de imagens com cache e no máximo 3 pedidos simultâneos
const imgCache = new Map();
let imgAtivos = 0;
const imgFila = [];
function fetchImagem(tipo, q) {
  const chave = `${tipo}:${q}`;
  if (imgCache.has(chave)) return imgCache.get(chave);
  const p = new Promise((resolve) => {
    const rodar = () => {
      imgAtivos++;
      fetch(`/api/imagem?tipo=${tipo}&q=${encodeURIComponent(q)}`)
        .then(r => (r.ok ? r.json() : null)).catch(() => null)
        .then(resolve)
        .finally(() => { imgAtivos--; const prox = imgFila.shift(); if (prox) prox(); });
    };
    imgAtivos < 3 ? rodar() : imgFila.push(rodar);
  });
  imgCache.set(chave, p);
  return p;
}

function aplicarFundo(el, url) {
  if (!el || !url) return;
  const img = new Image();
  img.referrerPolicy = 'no-referrer';
  img.onload = () => { el.style.backgroundImage = `url("${url}")`; el.classList.add('loaded'); };
  img.src = url;   // se falhar, permanece o gradiente/ícone
}

// --- fotos dos políticos
const fotos = {};            // id -> {url, credito, link} | null  (presente = já resolvido)
const fotosPolling = new Set();

function setAvatar(el, pol) {
  if (!el) return;
  const f = fotos[pol.id];
  if (f && f.url) {
    el.classList.add('has-photo');
    el.innerHTML = `<img src="${escapeHtml(f.url)}" alt="Foto de ${escapeHtml(pol.nome)}" decoding="async">`;
    el.querySelector('img').onerror = () => { el.classList.remove('has-photo'); el.textContent = initials(pol.nome); };
  } else {
    el.classList.remove('has-photo');
    el.textContent = initials(pol.nome);
  }
}

function acharPolitico(id) { return Object.values(POLITICIANS).flat().find(p => p.id === id); }

// As fotos vêm do disco do servidor (instantâneas). As que ainda não foram baixadas aparecem aos poucos.
async function carregarFotos(lista, tentativa = 0) {
  const ids = lista.map(p => p.id).filter(id => !(id in fotos) && !fotosPolling.has(id));
  if (!ids.length) return;
  ids.forEach(id => fotosPolling.add(id));
  let pendentes = [];
  try {
    const r = await fetch(`/api/fotos?ids=${ids.join(',')}`);
    const data = r.ok ? await r.json() : {};
    ids.forEach(id => {
      const d = data[String(id)];
      if (d && d.pendente) { pendentes.push(id); return; }
      fotos[id] = d || null;
      const pol = acharPolitico(id);
      if (!pol) return;
      document.querySelectorAll(`.avatar[data-id="${id}"]`).forEach(el => setAvatar(el, pol));
      if (selectedPolitician && selectedPolitician.id === id) setAvatar($('#panelAvatar'), pol);
    });
  } catch (_) { pendentes = ids.slice(); }
  ids.forEach(id => fotosPolling.delete(id));
  if (pendentes.length && tentativa < 150) {
    setTimeout(() => carregarFotos(pendentes.map(acharPolitico).filter(Boolean), tentativa + 1), 1200);
  }
}

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
    <article class="politician-card${selectedPolitician && selectedPolitician.id === pol.id ? ' selected' : ''}" data-id="${pol.id}">
      <div class="avatar" data-id="${pol.id}">${initials(pol.nome)}</div>
      <h3>${escapeHtml(pol.nome)}</h3>
      <p>${escapeHtml(pol.cargo)} · ${escapeHtml(pol.uf)}</p>
      <div class="card-tags">${escapeHtml(pol.partido)} · desde ${escapeHtml(pol.desde)}</div>
    </article>`).join('') : '<div class="empty">Nenhum político encontrado.</div>';

  list.forEach(pol => setAvatar(grid.querySelector(`.avatar[data-id="${pol.id}"]`), pol));
  carregarFotos(list);

  grid.querySelectorAll('.politician-card').forEach(card => {
    card.addEventListener('click', () => {
      const pol = list.find(p => String(p.id) === card.dataset.id);
      if (pol) selectPolitician(pol);
    });
  });
}

async function readJson(res) {
  let data = null;
  try { data = await res.json(); } catch (_) { /* resposta sem JSON */ }
  if (!res.ok) throw new Error((data && data.error) || `Falha na requisição (HTTP ${res.status})`);
  return data || {};
}

async function selectPolitician(pol) {
  selectedPolitician = pol;
  statusFilter = 'todos';
  renderPoliticians();
  $('#workspace').hidden = false;
  setAvatar($('#panelAvatar'), pol);
  $('#panelName').textContent = pol.nome;
  $('#panelInfo').textContent = `${pol.cargo} · ${pol.partido} · ${pol.uf} · desde ${pol.desde}`;
  $('#results').innerHTML = '';
  $('#workspace').scrollIntoView({ behavior: 'smooth', block: 'start' });

  // 1) Mostra NA HORA o que já está salvo no banco.
  const token = ++requestToken;
  let cache = null;
  try {
    cache = await readJson(await fetch(`/api/promessas/${pol.id}`, { cache: 'no-store' }));
    if (token !== requestToken) return;
    if (Object.keys(cache.temas || {}).length) renderResults(cache);
  } catch (e) { /* sem cache: segue para a busca */ }

  // 2) Só analisa automaticamente na primeira vez (quando não há nada salvo).
  // Artigos pendentes ficam para o botão "atualizar", evitando gasto inesperado de tokens.
  const semNada = !cache || !Object.keys(cache.temas || {}).length;
  if (semNada) {
    buscarTodasAsPropostas();
  }
}

async function buscarTodasAsPropostas(force = false) {
  if (!selectedPolitician) return;
  const token = ++requestToken;
  const pol = selectedPolitician;

  $('#loading').hidden = false;
  $('#btnBuscar').disabled = true;

  try {
    const res = await fetch('/api/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: pol.id, politician: pol.nome, force })
    });
    const data = await readJson(res);
    if (token !== requestToken) return;
    renderResults(data);
  } catch (e) {
    if (token !== requestToken) return;
    const jaTemResultado = $('#results').querySelector('.tema-bloco');
    const aviso = `<div class="error-box">❌ ${escapeHtml(e.message)}</div>`;
    if (jaTemResultado) $('#results').insertAdjacentHTML('afterbegin', aviso);
    else $('#results').innerHTML = aviso;
  } finally {
    if (token === requestToken) {
      $('#loading').hidden = true;
      $('#btnBuscar').disabled = false;
    }
  }
}

// Imagem de CADA proposta (id_promessa -> {url, credito, link}) e seu status ('ok' | 'none' | null = ainda buscando).
const imagensPromessa = {};
const imagemStatus = {};
const imagensEmAndamento = new Set();
let modalPromessaId = null;

function registrarImagens(temasDict) {
  Object.values(temasDict || {}).forEach(lista => lista.forEach(p => {
    if (p.imagem && p.imagem.url) imagensPromessa[p.id_promessa] = p.imagem;
    imagemStatus[p.id_promessa] = p.imagem_status || (p.imagem ? 'ok' : null);
  }));
}

function aplicarImagensPromessas(root) {
  root.querySelectorAll('.proposta-thumb[data-pid]').forEach(el => {
    const id = el.dataset.pid, img = imagensPromessa[id];
    if (img) {
      if (el.dataset.imgUrl === img.url) return;
      el.dataset.imgUrl = img.url;
      const teste = new Image();
      teste.onload = () => {
        el.style.backgroundImage = `url("${img.url}")`;
        el.classList.remove('skeleton', 'sem-imagem');
      };
      teste.onerror = () => {
        el.style.backgroundImage = '';
        el.classList.remove('skeleton');
        el.classList.add('sem-imagem');
      };
      teste.src = img.url;
    } else if (imagemStatus[id] === 'none') {
      el.style.backgroundImage = '';
      el.classList.remove('skeleton');
      el.classList.add('sem-imagem');           // esgotou as tentativas: fundo temático, não card vazio
    }
  });
}

// Pede ao servidor que escolha/baixe as imagens que faltam (em lotes pequenos) e preenche os cards aos poucos.
const imagensTentativas = {};
async function solicitarImagens(pol, rodada = 0) {
  if (imagensEmAndamento.has(pol.id) || rodada > 12) return;
  if (rodada === 0 && (imagensTentativas[pol.id] = (imagensTentativas[pol.id] || 0) + 1) > 4) return;
  imagensEmAndamento.add(pol.id);
  let continuar = false;
  try {
    const res = await fetch(`/api/imagens/${pol.id}`, { method: 'POST' });
    if (res.ok) {
      const data = await res.json();
      registrarImagens(data.temas);
      if (selectedPolitician && selectedPolitician.id === pol.id) {
        aplicarImagensPromessas($('#results'));
        atualizarBannerDoModal();
      }
      continuar = data.imagens_pendentes > 0 && data.imagens_decididas > 0;   // só repete se houve progresso
    }
  } catch (_) { /* sem rede: tenta novamente na próxima abertura */ }
  finally { imagensEmAndamento.delete(pol.id); }
  if (continuar) solicitarImagens(pol, rodada + 1);
}

function statusClass(status = '') {
  const s = status.toLowerCase();
  if (s.includes('parcial')) return 'status-parcialmente';
  if (s.includes('andamento')) return 'status-andamento';
  if (s.includes('não') || s.includes('nao')) return s.includes('verific') ? 'status-verificada' : 'status-nao';
  if (s.includes('cumprida')) return 'status-cumprida';
  return 'status-verificada';
}

function verifClass(v = '') {
  if (['oficial', 'checagem', 'corroborada'].includes(v)) return 'verif-boa';
  if (v === 'fonte_unica') return 'verif-media';
  if (['divergente', 'fonte_unica_negativa', 'fonte_baixa', 'modo_critico'].includes(v)) return 'verif-alerta';
  return 'verif-neutra';
}

function verifLabel(v = '', conf = 0) {
  const labels = {
    oficial: 'Fonte oficial',
    checagem: 'Checagem',
    corroborada: '2+ fontes',
    fonte_unica: 'Fonte única',
    fonte_unica_negativa: 'Evidência insuficiente',
    fonte_baixa: 'Fonte frágil',
    modo_critico: 'Modo crítico',
    extracao_local: 'Extração local',
    divergente: 'Fontes divergentes',
    sem_evidencia: 'Sem evidência'
  };
  return (labels[v] || v || 'Sem verificação') + (conf ? ` · ${conf}%` : '');
}

function tierLabel(t) {
  return ({1: 'Oficial', 2: 'Checagem', 3: 'Imprensa', 4: 'Partidária/Desconhecida', 5: 'Rede social'})[t] || 'Fonte';
}

let modalToken = 0;
let modalCidadeImg = null;
let modalCreditos = [];

function addCreditoModal(d) {
  if (!d || !d.credito) return;
  const item = d.link ? `<a href="${escapeHtml(d.link)}" target="_blank" rel="noopener">${escapeHtml(d.credito)}</a>` : escapeHtml(d.credito);
  if (modalCreditos.includes(item)) return;
  modalCreditos.push(item);
  $('#modalCreditos').innerHTML = modalCreditos.join(' · ');
}

// O banner é a imagem da PRÓPRIA proposta. Enquanto ela é buscada aparece um esqueleto cinza animado (nunca uma imagem genérica).
function atualizarBannerDoModal() {
  if (modalPromessaId === null) return;
  const hero = $('#modalHeroBg');
  const img = imagensPromessa[modalPromessaId];
  if (img) {
    hero.style.backgroundImage = `url("${img.url}")`;
    hero.classList.remove('skeleton');
    addCreditoModal(img);
  } else if (imagemStatus[modalPromessaId] === 'none') {
    hero.classList.remove('skeleton');
    if (modalCidadeImg) hero.style.backgroundImage = `url("${modalCidadeImg.url}")`;   // sem imagem da proposta: usa a da cidade
  } else {
    hero.classList.add('skeleton');
  }
}

function abrirModal(promessa, tema) {
  const token = ++modalToken;
  const pol = selectedPolitician;
  const cidade = cidadeDoPolitico(pol);
  modalPromessaId = promessa.id_promessa;
  modalCidadeImg = null;
  modalCreditos = [];

  $('#modalHeroBg').style.backgroundImage = '';
  const cityImg = $('#modalCityImg');
  cityImg.style.backgroundImage = '';
  cityImg.classList.remove('loaded');
  $('#modalCityLabel').textContent = `📍 ${cidade}${pol.uf && pol.uf !== 'BR' && cidade !== 'Brasília' ? ' · ' + pol.uf : ''}`;
  $('#modalCreditos').textContent = '';
  setAvatar($('#modalAvatar'), pol);
  atualizarBannerDoModal();

  // Foto da cidade (miniatura): vem do disco do servidor depois da 1ª busca.
  fetchImagem('cidade', cidade).then(d => {
    if (token !== modalToken || !d || !d.url) return;
    modalCidadeImg = d;
    cityImg.style.backgroundImage = `url("${d.url}")`;
    cityImg.classList.add('loaded');
    addCreditoModal(d);
    atualizarBannerDoModal();
  });
  const fotoEl = $('#modalAvatar img');
  if (fotoEl && fotos[pol.id]) {
    if (fotoEl.complete && fotoEl.naturalWidth) addCreditoModal(fotos[pol.id]);
    else fotoEl.addEventListener('load', () => addCreditoModal(fotos[pol.id]));
  }
  // Se a imagem desta proposta ainda não chegou, garante que a busca está rodando.
  if (!imagensPromessa[promessa.id_promessa] && imagemStatus[promessa.id_promessa] !== 'none') solicitarImagens(pol);

  $('#modalCandidato').textContent = pol.nome;
  $('#modalTituloProposta').textContent = promessa.titulo || promessa.promessa;
  $('#modalDescricao').textContent = promessa.descricao || promessa.justificativa || 'Descrição indisponível.';

  const motivoEl = $('#modalMotivo');
  if (motivoEl) {
    motivoEl.textContent = promessa.status_motivo ? `Por quê: ${promessa.status_motivo}` : '';
    motivoEl.style.display = promessa.status_motivo ? 'block' : 'none';
  }

  const statusEl = $('#modalStatus');
  statusEl.textContent = promessa.status || 'Não verificada';
  statusEl.className = `status ${statusClass(promessa.status)}`;

  const fonteEl = $('#modalFonte');
  if (promessa.fonte_url) {
    fonteEl.style.display = 'block';
    fonteEl.href = promessa.fonte_url;
    fonteEl.textContent = `Acessar: ${promessa.fonte_site || 'Fonte'} \u2197`;
  } else {
    fonteEl.style.display = 'none';
  }

  const vBox = $('#modalVerificacao');
  if (vBox) {
    if (promessa.verificacao) {
      vBox.style.display = 'block';
      const badge = $('#modalVerifBadge');
      badge.className = `verif ${verifClass(promessa.verificacao)}`;
      badge.textContent = verifLabel(promessa.verificacao, promessa.confianca);
      $('#modalVerifMotivo').textContent = promessa.motivo_verificacao || '';
      const plano = $('#modalVerifPlano');
      if (promessa.promessa_oficial === 1) plano.textContent = 'Promessa consta no plano de governo oficial.';
      else if (promessa.promessa_oficial === 0) plano.textContent = 'Promessa não localizada no plano de governo oficial.';
      else plano.textContent = 'Plano de governo oficial não localizado para este político.';
      const ul = $('#modalVerifFontes');
      ul.innerHTML = (promessa.fontes_verificacao || []).slice(0, 6).map(f =>
        `<li><span class="tier tier-${Number(f.tier) || 4}">${tierLabel(f.tier)}</span> ` +
        `<a href="${escapeHtml(f.url)}" target="_blank" rel="noopener">${escapeHtml(f.nome || f.dominio || 'Fonte')}</a></li>`
      ).join('');
    } else {
      vBox.style.display = 'none';
    }
  }

  $('#propostaModal').style.display = 'flex';
}

function fecharModal() {
  modalToken++; modalPromessaId = null;
  $('#propostaModal').style.display = 'none';
}

function formatarData(iso) {
  if (!iso) return '';
  const d = new Date(iso.replace(' ', 'T') + 'Z');
  return isNaN(d) ? iso : d.toLocaleString('pt-BR');
}

function renderResults(data) {
  lastData = data;
  if (data.error) {
    $('#results').innerHTML = `<div class="error-box">❌ ${escapeHtml(data.error)}</div>`;
    return;
  }

  const temasDict = data.temas || {};
  const temasNomes = Object.keys(temasDict).filter(t => (temasDict[t] || []).length);

  if (temasNomes.length === 0) {
    $('#results').innerHTML = '<div class="empty">Nenhuma promessa encontrada para este político.</div>';
    return;
  }

  // contagem por status, para os filtros
  const contagem = { todos: 0 };
  temasNomes.forEach(t => temasDict[t].forEach(p => {
    const st = p.status || 'não verificada';
    contagem.todos++;
    contagem[st] = (contagem[st] || 0) + 1;
  }));

  const sites = (data.sites_consultados || []);
  const sitesTxt = sites.length ? ` · ${sites.length} fontes` : '';
  const atualizado = data.ultima_busca ? ` · atualizado em ${formatarData(data.ultima_busca)}` : '';
  const novos = (data.novas_propostas || data.propostas_atualizadas)
    ? `<p class="results-delta">${data.plano_encontrado ? 'Plano de governo localizado · ' : ''}+${data.novas_propostas || 0} novas propostas · ${data.propostas_atualizadas || 0} atualizadas nesta busca</p>` : '';
  const pend = data.artigos_pendentes > 0
    ? `<p class="results-delta">${data.artigos_pendentes} artigos salvos aguardam análise — clique em atualizar para continuar.</p>` : '';

  let html = `<div class="results-header">
                <h3>${contagem.todos} propostas e promessas encontradas</h3>
                <p>${data.total_artigos_analisados || 0} artigos/documentos no banco${sitesTxt}${atualizado}</p>
                ${novos}${pend}
              </div>`;

  if (data.resumo_geral) html += `<div class="summary">📌 ${escapeHtml(data.resumo_geral)}</div>`;

  const chips = Object.keys(contagem).map(k => `
      <button type="button" class="chip${statusFilter === k ? ' active' : ''}" data-status="${escapeHtml(k)}">
        ${k === 'todos' ? 'Todas' : escapeHtml(k)} (${contagem[k]})
      </button>`).join('');
  html += `<div class="chips">${chips}</div>`;

  const container = document.createElement('div');
  container.innerHTML = html;

  temasNomes.forEach(tema => {
    const propostas = temasDict[tema]
      .map((p, idx) => ({ p, idx }))
      .filter(({ p }) => statusFilter === 'todos' || (p.status || 'não verificada') === statusFilter);
    if (!propostas.length) return;

    const bloco = document.createElement('div');
    bloco.className = 'tema-bloco';

    let propostasHtml = '<div class="propostas-grid">';
    propostas.forEach(({ p, idx }) => {
      propostasHtml += `
        <div class="proposta-quadrado" data-tema="${escapeHtml(tema)}" data-idx="${idx}">
          <div class="proposta-thumb ${(p.imagem && p.imagem.url) ? '' : (p.imagem_status === 'none' ? 'sem-imagem' : 'skeleton')}" data-pid="${p.id_promessa}"${(p.imagem && p.imagem.url) ? ` style="background-image:url('${escapeHtml(p.imagem.url)}')"` : ''}></div>
          <div class="proposta-body">
            <h4>${escapeHtml(p.titulo || p.promessa)}</h4>
            ${p.origem === 'plano' ? '<small class="origem">Plano de governo</small>' : (p.origem === 'extracao_local' ? '<small class="origem">Extração local</small>' : '')}
            <div class="card-badges">
              <span class="status ${statusClass(p.status)}">${escapeHtml(p.status || 'Indefinido')}</span>
              ${p.verificacao ? `<span class="verif ${verifClass(p.verificacao)}" title="${escapeHtml(p.motivo_verificacao || '')}">${verifLabel(p.verificacao, p.confianca)}</span>` : ''}
            </div>
          </div>
        </div>`;
    });
    propostasHtml += '</div>';
    bloco.innerHTML = `<h3>${escapeHtml(tema)} <small>(${propostas.length})</small></h3>${propostasHtml}`;
    container.appendChild(bloco);
  });

  $('#results').innerHTML = '';
  $('#results').appendChild(container);

  registrarImagens(temasDict);
  aplicarImagensPromessas($('#results'));
  const semImagemAgora = Object.values(temasDict).flat().filter(p => !p.imagem).length;
  if (semImagemAgora > 0 && selectedPolitician) solicitarImagens(selectedPolitician);
  setTimeout(() => {
    $('#results').querySelectorAll('.proposta-thumb.skeleton').forEach(el => {
      if (!imagensPromessa[el.dataset.pid]) {
        el.classList.remove('skeleton');
        el.classList.add('sem-imagem');
      }
    });
  }, 12000);

  $('#results').querySelectorAll('.chip').forEach(chip => {
    chip.addEventListener('click', () => { statusFilter = chip.dataset.status; renderResults(lastData); });
  });
  $('#results').querySelectorAll('.proposta-quadrado').forEach(card => {
    card.addEventListener('click', () => {
      abrirModal(temasDict[card.dataset.tema][Number(card.dataset.idx)], card.dataset.tema);
    });
  });
}

// Eventos
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
$('#btnBuscar').addEventListener('click', () => buscarTodasAsPropostas(true));
$('#propostaModal').addEventListener('click', (e) => {
  if (e.target === $('#propostaModal')) fecharModal();
});
document.addEventListener('keydown', (e) => { if (e.key === 'Escape') fecharModal(); });

renderPoliticians();
