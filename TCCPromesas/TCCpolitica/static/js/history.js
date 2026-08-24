const escapeHtml = (value = '') => String(value).replace(/[&<>'"]/g, (char) => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[char]));

async function loadHistory() {
  const container = document.querySelector('#historyResults');
  try {
    const response = await fetch(`/api/politicians/${encodeURIComponent(window.POLITICIAN_ID)}/history`);
    const data = await response.json();
    if (data.error) throw new Error(data.error);
    if (!data.promessas.length) { container.innerHTML = '<div class="empty">Este político ainda não possui promessas oficiais importadas.</div>'; return; }
    container.innerHTML = data.promessas.map((promise) => `
      <article class="history-card">
        <h3>${escapeHtml(promise.promessa)}</h3>
        <p>${escapeHtml(promise.explicacao || promise.resumo || 'Ainda não há uma análise registrada.')}</p>
        <span class="status status-verificada">${escapeHtml(promise.status)}</span>
        <div class="history-track">${promise.historico.length ? promise.historico.map((event) => `<div class="history-event"><strong>${escapeHtml(event.status)}</strong>${new Date(event.data).toLocaleDateString('pt-BR')}</div>`).join('') : '<div class="history-event">Nenhuma checagem registrada</div>'}</div>
      </article>`).join('');
  } catch (error) { container.innerHTML = `<div class="notice">Não foi possível carregar o histórico: ${escapeHtml(error.message)}</div>`; }
}
loadHistory();
