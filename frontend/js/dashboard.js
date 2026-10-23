let todasAssinaturas = [];      // somente a página atual da listagem
let proximasRenovacoes = [];    // agenda completa (independe da paginação)
let assinaturasFiltradas = [];
let editandoId = null;
let buscaDebounce = null;
let chartCategoria = null;
let chartPagamento = null;
let paginaAtual = 1;
let totalPaginas = 1;
const LIMITE_PAGINA = 10;

const PERIODICIDADE_LABEL = { semanal: 'Semanal', mensal: 'Mensal', anual: 'Anual' };
const FATOR_ANUAL_JS = { semanal: 52, mensal: 12, anual: 1 };

const METODOS_PAGAMENTO_LABEL = {
  cartao_credito: 'Cartão de crédito',
  cartao_debito: 'Cartão de débito',
  pix: 'PIX',
  boleto: 'Boleto',
  debito_automatico: 'Débito automático',
  transferencia: 'Transferência',
  outro: 'Outro'
};

const CORES_GRAFICO = ['#2563EB', '#0EA5E9', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#6366F1', '#14B8A6', '#F97316'];

function valorAnualizado(a) {
  const f = FATOR_ANUAL_JS[a.periodicidade] || 12;
  return a.valor_anualizado != null ? a.valor_anualizado : a.valor_mensal * f;
}

function formatarMoeda(valor) {
  return valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

function diasAteRenovacao(dataStr) {
  const hoje = new Date();
  hoje.setHours(0, 0, 0, 0);
  const renovacao = new Date(dataStr + 'T00:00:00');
  return Math.ceil((renovacao - hoje) / (1000 * 60 * 60 * 24));
}

// ── Fetch com filtros ──────────────────────────────────────────────
function montarQueryString() {
  const params = new URLSearchParams();
  const busca = document.getElementById('filtro-busca').value.trim();
  const idCat = document.getElementById('filtro-categoria').value;
  const pagamento = document.getElementById('filtro-pagamento').value;
  const periodicidadeEl = document.getElementById('filtro-periodicidade')?.value || '';
  const statusEl = document.getElementById('filtro-status').value;
  const ordenar = document.getElementById('filtro-ordenar').value;

  if (busca) params.set('busca', busca);
  if (idCat) params.set('id_categoria', idCat);
  if (pagamento) params.set('metodo_pagamento', pagamento);
  if (periodicidadeEl) params.set('periodicidade', periodicidadeEl);
  if (statusEl !== 'todas') params.set('status', statusEl);
  if (ordenar) {
    const last = ordenar.lastIndexOf('_');
    params.set('ordenar_por', ordenar.slice(0, last));
    params.set('ordem', ordenar.slice(last + 1));
  }
  params.set('page', String(paginaAtual));
  params.set('limit', String(LIMITE_PAGINA));
  const qs = params.toString();
  return qs ? `?${qs}` : '';
}

async function carregarAssinaturas() {
  try {
    const qs = montarQueryString();
    const res = await apiFetch(`/assinaturas${qs}`);
    const payload = await res.json();
    if (payload && payload.paginacao) {
      todasAssinaturas = payload.assinaturas || [];
      totalPaginas = payload.paginacao.total_paginas || 1;
      paginaAtual = payload.paginacao.page || 1;
    } else {
      todasAssinaturas = Array.isArray(payload) ? payload : [];
      totalPaginas = 1;
    }
    assinaturasFiltradas = todasAssinaturas;
    renderizarAssinaturas();
    renderizarPaginacao();
  } catch {
    document.getElementById('assinaturas-list').innerHTML = '<div class="empty">Erro ao carregar assinaturas.</div>';
  }
}

// Próximas renovações, notificações e calendário usam todas as assinaturas
// ativas (/assinaturas/proximas), não só a página exibida na listagem.
async function carregarAgenda() {
  try {
    const res = await apiFetch('/assinaturas/proximas');
    if (!res.ok) throw new Error('Falha ao carregar agenda');
    proximasRenovacoes = await res.json();
  } catch {
    proximasRenovacoes = [];
  }
  renderizarRenovacoes();
  atualizarNotificacoes();
  if (typeof renderizarCalendario === 'function') renderizarCalendario();
}

async function carregarEstatisticas() {
  try {
    const res = await apiFetch('/assinaturas/estatisticas');
    const dados = await res.json();
    ultimasEstatisticas = dados;
    renderizarStats(dados);
    renderizarGraficos(dados);
  } catch {
    // silencioso — stats são secundários
  }
}

function renderizarStats(dados) {
  const row = document.getElementById('stats-row');
  row.style.display = '';
  document.getElementById('total-mensal').textContent = formatarMoeda(dados.total_mensal || 0);
  const totalAnual = dados.total_anual != null ? dados.total_anual : (dados.total_mensal * 12);
  document.getElementById('stat-anual').textContent = formatarMoeda(totalAnual);
  const media = dados.media_anual != null ? dados.media_anual : (dados.total_ativas > 0 ? totalAnual / dados.total_ativas : 0);
  document.getElementById('stat-media').textContent = formatarMoeda(media);
  const catCara = dados.categoria_mais_cara;
  document.getElementById('stat-cat-cara').textContent = catCara ? catCara.nome_categoria : '—';
  const sub = document.getElementById('stat-cat-cara-sub');
  if (sub) sub.textContent = catCara ? `${formatarMoeda(catCara.total_anual || catCara.total || 0)} / ano` : '';
  const hint = document.getElementById('summary-anual-hint');
  if (hint) { hint.textContent = `Você gasta ${formatarMoeda(totalAnual)} por ano`; hint.style.display = ''; }
}

let ultimasEstatisticas = null;

function corCss(nome) {
  return getComputedStyle(document.documentElement).getPropertyValue(nome).trim();
}

// Gráficos seguem as cores do tema (texto, grade, tooltip)
function aplicarTemaGraficos() {
  Chart.defaults.color = corCss('--text-muted');
  Chart.defaults.borderColor = corCss('--divider');
}

document.addEventListener('temachange', () => {
  if (ultimasEstatisticas && typeof Chart !== 'undefined') renderizarGraficos(ultimasEstatisticas);
});

function renderizarGraficos(dados) {
  aplicarTemaGraficos();
  const grid = document.getElementById('charts-grid');
  grid.style.display = '';

  // Categoria
  const catCanvas = document.getElementById('chart-categoria');
  const catEmpty = document.getElementById('chart-categoria-empty');
  if (dados.por_categoria.length === 0) {
    catCanvas.style.display = 'none';
    catEmpty.style.display = '';
  } else {
    catEmpty.style.display = 'none';
    catCanvas.style.display = '';
    if (chartCategoria) chartCategoria.destroy();
    chartCategoria = new Chart(catCanvas, {
      type: 'doughnut',
      data: {
        labels: dados.por_categoria.map(c => c.nome_categoria),
        datasets: [{
          data: dados.por_categoria.map(c => c.total),
          backgroundColor: dados.por_categoria.map((_, i) => CORES_GRAFICO[i % CORES_GRAFICO.length]),
          borderWidth: 2,
          borderColor: corCss('--white'),
          hoverOffset: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '62%',
        plugins: {
          legend: { position: 'bottom', labels: { usePointStyle: true, padding: 14, font: { family: 'Inter', size: 11 } } },
          tooltip: { callbacks: { label: ctx => ` ${ctx.label}: ${formatarMoeda(ctx.parsed)}` } }
        }
      }
    });
  }

  // Pagamento
  const pagCanvas = document.getElementById('chart-pagamento');
  const pagEmpty = document.getElementById('chart-pagamento-empty');
  if (dados.por_pagamento.length === 0) {
    pagCanvas.style.display = 'none';
    pagEmpty.style.display = '';
  } else {
    pagEmpty.style.display = 'none';
    pagCanvas.style.display = '';
    if (chartPagamento) chartPagamento.destroy();
    chartPagamento = new Chart(pagCanvas, {
      type: 'bar',
      data: {
        labels: dados.por_pagamento.map(p => METODOS_PAGAMENTO_LABEL[p.metodo] || p.metodo),
        datasets: [{
          label: 'Gasto mensal',
          data: dados.por_pagamento.map(p => p.total),
          backgroundColor: corCss('--blue'),
          borderRadius: 8,
          barThickness: 22
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: { callbacks: { label: ctx => ` ${formatarMoeda(ctx.parsed.y)}` } }
        },
        scales: {
          y: { beginAtZero: true, ticks: { callback: v => `R$ ${v}`, font: { family: 'Inter', size: 11 } }, grid: { color: corCss('--divider') } },
          x: { ticks: { font: { family: 'Inter', size: 11 } }, grid: { display: false } }
        }
      }
    });
  }
}

// ── Filtros / busca ───────────────────────────────────────────────
function onBuscaInput() {
  const val = document.getElementById('filtro-busca').value;
  document.getElementById('btn-clear-busca').style.display = val ? '' : 'none';
  clearTimeout(buscaDebounce);
  buscaDebounce = setTimeout(() => { paginaAtual = 1; carregarAssinaturas(); }, 300);
}

function limparBusca() {
  document.getElementById('filtro-busca').value = '';
  document.getElementById('btn-clear-busca').style.display = 'none';
  paginaAtual = 1;
  carregarAssinaturas();
}

function aplicarFiltros() {
  paginaAtual = 1;
  carregarAssinaturas();
}

function renderizarPaginacao() {
  const wrap = document.getElementById('paginacao');
  const info = document.getElementById('paginacao-info');
  const btnPrev = document.getElementById('btn-pag-anterior');
  const btnNext = document.getElementById('btn-pag-proxima');
  if (!wrap) return;
  if (totalPaginas <= 1) { wrap.style.display = 'none'; return; }
  wrap.style.display = '';
  if (info) info.textContent = `Página ${paginaAtual} de ${totalPaginas}`;
  if (btnPrev) btnPrev.disabled = paginaAtual <= 1;
  if (btnNext) btnNext.disabled = paginaAtual >= totalPaginas;
}
function paginaAnterior() { if (paginaAtual > 1) { paginaAtual--; carregarAssinaturas(); } }
function proximaPagina() { if (paginaAtual < totalPaginas) { paginaAtual++; carregarAssinaturas(); } }

function renderizarRenovacoes() {
  const container = document.getElementById('renovacoes-list');
  const proximas = proximasRenovacoes
    .filter(a => a.proxima_renovacao && diasAteRenovacao(a.proxima_renovacao) >= 0)
    .slice(0, 4);

  if (proximas.length === 0) {
    container.innerHTML = '<div class="empty">Nenhuma renovação próxima.</div>';
    return;
  }

  container.innerHTML = proximas.map(a => {
    const dias = diasAteRenovacao(a.proxima_renovacao);
    const label = dias === 0 ? 'Renova hoje' : dias === 1 ? 'Renova amanhã' : `Renova em ${dias} dias`;
    const urgente = dias <= 3 ? ' style="color:var(--red);font-weight:600;"' : '';
    return `
      <div class="renewal-item">
        <div class="service-logo">
          <img src="${logoUrl(a.nome_servico)}" alt="${escapar(a.nome_servico)}" data-inicial="${escapar(a.nome_servico[0])}" />
        </div>
        <div class="renewal-info">
          <div class="renewal-name">${escapar(a.nome_servico)}</div>
          <div class="renewal-days"${urgente}>${label}</div>
        </div>
        <div class="renewal-value">${formatarMoeda(a.valor_mensal)}</div>
      </div>`;
  }).join('');
}

function renderizarAssinaturas() {
  const container = document.getElementById('assinaturas-list');

  if (todasAssinaturas.length === 0) {
    const temFiltro = document.getElementById('filtro-busca').value.trim()
      || document.getElementById('filtro-categoria').value
      || document.getElementById('filtro-pagamento').value
      || document.getElementById('filtro-periodicidade').value
      || document.getElementById('filtro-status').value !== 'ativa';
    container.innerHTML = temFiltro
      ? '<div class="empty">Nenhum resultado para os filtros atuais.<br><button class="link" onclick="limparTodosFiltros()" style="margin-top:8px;background:none;border:none;cursor:pointer;color:var(--blue);font-weight:600;">Limpar filtros</button></div>'
      : '<div class="empty">Nenhuma assinatura encontrada. Que tal adicionar a primeira?</div>';
    return;
  }

  container.innerHTML = todasAssinaturas.map(a => {
    const badgeClass = a.status === 'ativa' ? 'badge-ativa' : 'badge-cancelada';
    const per = PERIODICIDADE_LABEL[a.periodicidade] || 'Mensal';
    const anual = formatarMoeda(valorAnualizado(a));
    return `
    <div class="sub-item">
      <div class="service-logo">
        <img src="${logoUrl(a.nome_servico)}" alt="${escapar(a.nome_servico)}" data-inicial="${escapar(a.nome_servico[0])}" />
      </div>
      <div class="sub-info">
        <div class="sub-name">${escapar(a.nome_servico)} <span class="badge ${badgeClass}" style="margin-left:6px;font-size:10px;">${a.status === 'ativa' ? 'Ativa' : 'Cancelada'}</span> <span class="badge" style="margin-left:4px;font-size:10px;background:var(--bg);border:1px solid var(--border);">${escapar(per)}</span></div>
        <div class="sub-category">${escapar(a.tipo_plano || 'Sem plano')} · ${METODOS_PAGAMENTO_LABEL[a.metodo_pagamento] || 'Pagamento não informado'} · ${anual}/ano</div>
      </div>
      <div class="sub-value">${formatarMoeda(a.valor_mensal)}</div>
      <div class="sub-actions">
        <button class="btn-icon" title="Histórico" onclick="abrirHistorico(${a.id_assinatura})">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
        </button>
        <button class="btn-icon" title="Editar" onclick="abrirModalEditar(${a.id_assinatura})">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
        </button>
        <button class="btn-icon danger" title="Excluir" onclick="excluirAssinatura(${a.id_assinatura})">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg>
        </button>
      </div>
    </div>`;
  }).join('');
}

function limparTodosFiltros() {
  document.getElementById('filtro-busca').value = '';
  document.getElementById('btn-clear-busca').style.display = 'none';
  document.getElementById('filtro-categoria').value = '';
  document.getElementById('filtro-pagamento').value = '';
  const perSel = document.getElementById('filtro-periodicidade'); if (perSel) perSel.value = '';
  document.getElementById('filtro-status').value = 'ativa';
  document.getElementById('filtro-ordenar').value = 'data_renovacao_asc';
  paginaAtual = 1;
  carregarAssinaturas();
}

// ── Notificações ──────────────────────────────────────────────────
const NOTIF_KEY = 'assinify_notif_lidas';
let notifStorageKey = NOTIF_KEY;

// Chave por assinatura + data: a mesma assinatura volta a notificar no ciclo seguinte.
function chaveNotif(a) { return `${a.id_assinatura}:${a.proxima_renovacao}`; }

function getNotifsLidas() {
  try { return JSON.parse(localStorage.getItem(notifStorageKey) || '[]'); } catch { return []; }
}
function setNotifsLidas(chaves) {
  try { localStorage.setItem(notifStorageKey, JSON.stringify(chaves)); } catch {}
}

function renovacoesProximas7Dias() {
  return proximasRenovacoes
    .filter(a => {
      if (!a.proxima_renovacao) return false;
      const dias = diasAteRenovacao(a.proxima_renovacao);
      return dias >= 0 && dias <= 7;
    })
    .sort((a, b) => diasAteRenovacao(a.proxima_renovacao) - diasAteRenovacao(b.proxima_renovacao));
}

function atualizarNotificacoes() {
  const badge = document.getElementById('notif-badge');
  const list = document.getElementById('notif-list');
  const lidas = getNotifsLidas();

  const pendentes = renovacoesProximas7Dias();
  const naoLidas = pendentes.filter(a => !lidas.includes(chaveNotif(a)));

  if (naoLidas.length > 0) {
    badge.textContent = naoLidas.length > 9 ? '9+' : String(naoLidas.length);
    badge.style.display = '';
  } else {
    badge.style.display = 'none';
  }

  if (pendentes.length === 0) {
    list.innerHTML = '<div class="notif-empty">Nenhuma renovação nos próximos 7 dias. Tudo em dia! 🎉</div>';
    return;
  }

  list.innerHTML = pendentes.map(a => {
    const dias = diasAteRenovacao(a.proxima_renovacao);
    const label = dias === 0 ? 'Vence hoje!' : dias === 1 ? 'Vence amanhã' : `Vence em ${dias} dias`;
    const isLida = lidas.includes(chaveNotif(a));
    const urgente = dias <= 2 ? ' notif-item-urgent' : '';
    return `
      <div class="notif-item${urgente}${isLida ? ' notif-item-read' : ''}">
        <div class="service-logo" style="width:32px;height:32px;border-radius:8px;">
          <img src="${logoUrl(a.nome_servico)}" alt="" data-inicial="${escapar(a.nome_servico[0])}" />
        </div>
        <div class="notif-item-info">
          <div class="notif-item-name">${escapar(a.nome_servico)}</div>
          <div class="notif-item-meta">${label} · ${formatarMoeda(a.valor_mensal)} · ${escapar(a.proxima_renovacao)}</div>
        </div>
        ${isLida ? '<span class="notif-check">✓</span>' : ''}
      </div>`;
  }).join('');
}

function toggleNotif() {
  const dd = document.getElementById('notif-dropdown');
  dd.classList.toggle('open');
}

function marcarNotifsLidas() {
  setNotifsLidas(renovacoesProximas7Dias().map(chaveNotif));
  atualizarNotificacoes();
}

document.addEventListener('click', (e) => {
  const wrapper = document.getElementById('notif-wrapper');
  if (!wrapper.contains(e.target)) {
    document.getElementById('notif-dropdown').classList.remove('open');
  }
});

// ── Categorias (filtro + modal) ───────────────────────────────────
async function carregarCategorias() {
  try {
    const res = await apiFetch('/categorias');
    if (!res.ok) throw new Error('Falha ao carregar categorias');
    const categorias = await res.json();
    const opts = categorias.map(c => `<option value="${c.id_categoria}">${escapar(c.nome_categoria)}</option>`).join('');
    document.getElementById('filtro-categoria').innerHTML = '<option value="">Todas as categorias</option>' + opts;
    document.getElementById('input-categoria').innerHTML = opts;
  } catch {
    console.error('Erro ao carregar categorias');
  }
}

function atualizarPreviewAnualizado() {
  const v = parseFloat(document.getElementById('input-valor').value) || 0;
  const per = document.getElementById('input-periodicidade')?.value || 'mensal';
  const f = FATOR_ANUAL_JS[per] || 12;
  const el = document.getElementById('preview-anualizado-valor');
  if (el) el.textContent = v ? formatarMoeda(v * f) : '—';
}

function abrirModal() {
  editandoId = null;
  document.getElementById('modal-title').textContent = 'Nova assinatura';
  document.getElementById('input-nome').value = '';
  document.getElementById('input-valor').value = '';
  document.getElementById('input-periodicidade').value = 'mensal';
  document.getElementById('input-renovacao').value = '';
  document.getElementById('input-plano').value = '';
  document.getElementById('input-pagamento').value = 'cartao_credito';
  document.getElementById('input-status').value = 'ativa';
  atualizarPreviewAnualizado();
  document.getElementById('modal').classList.add('open');
}

function abrirModalEditar(id) {
  const a = todasAssinaturas.find(x => x.id_assinatura === id);
  if (!a) return;
  editandoId = id;
  document.getElementById('modal-title').textContent = 'Editar assinatura';
  document.getElementById('input-nome').value = a.nome_servico;
  document.getElementById('input-valor').value = a.valor_mensal;
  document.getElementById('input-periodicidade').value = a.periodicidade || 'mensal';
  document.getElementById('input-renovacao').value = a.data_renovacao;
  document.getElementById('input-plano').value = a.tipo_plano || '';
  document.getElementById('input-pagamento').value = a.metodo_pagamento || 'cartao_credito';
  document.getElementById('input-status').value = a.status || 'ativa';
  atualizarPreviewAnualizado();
  document.getElementById('input-categoria').value = a.id_categoria;
  document.getElementById('modal').classList.add('open');
}

function fecharModal() {
  document.getElementById('modal').classList.remove('open');
}

function fecharModalFora(e) {
  if (e.target === document.getElementById('modal')) fecharModal();
}

async function salvarAssinatura() {
  const dados = {
    nome_servico: document.getElementById('input-nome').value,
    valor_mensal: parseFloat(document.getElementById('input-valor').value),
    periodicidade: document.getElementById('input-periodicidade').value,
    data_renovacao: document.getElementById('input-renovacao').value,
    tipo_plano: document.getElementById('input-plano').value,
    metodo_pagamento: document.getElementById('input-pagamento').value,
    id_categoria: parseInt(document.getElementById('input-categoria').value),
    status: document.getElementById('input-status').value
  };

  if (!dados.nome_servico || !dados.valor_mensal || !dados.data_renovacao) {
    alert('Preencha os campos obrigatórios.');
    return;
  }

  try {
    const url = editandoId ? `/assinaturas/${editandoId}` : '/assinaturas';
    const method = editandoId ? 'PUT' : 'POST';
    const res = await apiFetch(url, { method, body: JSON.stringify(dados) });

    if (res.ok) {
      fecharModal();
      carregarAssinaturas();
      carregarEstatisticas();
      carregarAgenda();
    } else {
      const err = await res.json();
      alert(err.erro || 'Erro ao salvar.');
    }
  } catch {
    alert('Erro de conexão com a API.');
  }
}

async function excluirAssinatura(id) {
  if (!confirm('Deseja excluir esta assinatura?')) return;
  try {
    const res = await apiFetch(`/assinaturas/${id}`, { method: 'DELETE' });
    if (res.ok) { carregarAssinaturas(); carregarEstatisticas(); carregarAgenda(); }
    else alert('Erro ao excluir.');
  } catch {
    alert('Erro de conexão com a API.');
  }
}

async function exportarCSV() {
  try {
    const qs = montarQueryString();
    const res = await apiFetch(`/assinaturas/exportar${qs}`);
    if (!res.ok) { const e = await res.json().catch(() => ({})); alert(e.erro || 'Erro ao exportar.'); return; }
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = 'assinaturas.csv';
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  } catch { alert('Erro de conexão ao exportar.'); }
}

const CAMPO_LABEL = { nome_servico: 'Nome', valor_mensal: 'Valor', periodicidade: 'Periodicidade', data_renovacao: 'Renovação', status: 'Status', tipo_plano: 'Plano', metodo_pagamento: 'Pagamento', id_categoria: 'Categoria' };
async function abrirHistorico(id) {
  const a = todasAssinaturas.find(x => x.id_assinatura === id);
  document.getElementById('historico-nome').textContent = a ? a.nome_servico : '';
  const box = document.getElementById('timeline-historico');
  box.innerHTML = '<div class="loading">Carregando...</div>';
  document.getElementById('modal-historico').classList.add('open');
  try {
    const res = await apiFetch(`/assinaturas/${id}/historico`);
    const itens = await res.json();
    if (!Array.isArray(itens) || itens.length === 0) { box.innerHTML = '<div class="empty">Nenhuma alteração registrada.</div>'; return; }
    box.innerHTML = '<div class="timeline">' + itens.map(h => {
      const campo = CAMPO_LABEL[h.campo] || h.campo;
      const quando = h.data_alteracao ? new Date(h.data_alteracao).toLocaleString('pt-BR') : '';
      return `<div class="timeline-item"><div class="timeline-dot"></div><div class="timeline-body"><div class="timeline-campo">${escapar(campo)}</div><div class="timeline-valores"><span class="timeline-antigo">${escapar(h.valor_antigo ?? '—')}</span> → <span class="timeline-novo">${escapar(h.valor_novo ?? '—')}</span></div><div class="timeline-data">${escapar(quando)}</div></div></div>`;
    }).join('') + '</div>';
  } catch { box.innerHTML = '<div class="empty">Erro ao carregar histórico.</div>'; }
}
function fecharHistorico() { document.getElementById('modal-historico').classList.remove('open'); }
function fecharHistoricoFora(e) { if (e.target === document.getElementById('modal-historico')) fecharHistorico(); }

async function init() {
  const usuario = await protegerPagina();
  if (!usuario) return;
  notifStorageKey = `${NOTIF_KEY}_${usuario.id_usuario}`;
  await carregarCategorias();
  carregarAssinaturas();
  carregarEstatisticas();
  carregarAgenda();
  // preview anualizado reativo
  document.getElementById('input-valor')?.addEventListener('input', atualizarPreviewAnualizado);
  document.getElementById('input-periodicidade')?.addEventListener('change', atualizarPreviewAnualizado);
}

init();