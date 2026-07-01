const API = 'http://localhost:5000';
const LOGO_TOKEN = 'pk_aFebUAI6TXi3KllA2BUauA';

let todasAssinaturas = [];
let editandoId = null;

function getIdUsuario() {
  return parseInt(document.getElementById('select-usuario').value);
}

async function carregarUsuariosSelect() {
  try {
    const res = await fetch(`${API}/usuarios`);
    const usuarios = await res.json();
    const select = document.getElementById('select-usuario');

    select.innerHTML = usuarios.map(u =>
      `<option value="${u.id_usuario}">${u.nome}</option>`
    ).join('');

    const idSalvo = localStorage.getItem('assinify_usuario_id');
    const usuarioSalvo = idSalvo ? usuarios.find(u => u.id_usuario === parseInt(idSalvo)) : null;
    const usuarioAtivo = usuarioSalvo || usuarios[0];

    if (usuarioAtivo) {
      select.value = usuarioAtivo.id_usuario;
      atualizarSidebarUsuario(usuarioAtivo);
    }

    select.addEventListener('change', () => {
      const u = usuarios.find(x => x.id_usuario === parseInt(select.value));
      if (u) {
        localStorage.setItem('assinify_usuario_id', u.id_usuario);
        atualizarSidebarUsuario(u);
        carregarAssinaturas();
      }
    });
  } catch {
    console.error('Erro ao carregar usuários');
  }
}

function atualizarSidebarUsuario(u) {
  if (!u) return;
  document.getElementById('sidebar-avatar').textContent = u.nome[0].toUpperCase();
  document.getElementById('sidebar-nome').textContent = u.nome;
}

function logoUrl(nome) {
  const limpo = nome.toLowerCase()
    .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9\s]/g, '')
    .trim()
    .split(/\s+/)[0];
  return `https://img.logo.dev/${limpo}.com?token=${LOGO_TOKEN}&format=webp&retina=true`;
}

function formatarMoeda(valor) {
  return valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

function diasAteRenovacao(dataStr) {
  const hoje = new Date();
  const renovacao = new Date(dataStr + 'T00:00:00');
  return Math.ceil((renovacao - hoje) / (1000 * 60 * 60 * 24));
}

async function carregarAssinaturas() {
  try {
    const res = await fetch(`${API}/assinaturas`);
    todasAssinaturas = await res.json();
    renderizarAssinaturas();
    renderizarRenovacoes();
    calcularTotal();
  } catch {
    document.getElementById('assinaturas-list').innerHTML = '<div class="empty">Erro ao carregar assinaturas.</div>';
  }
}

function calcularTotal() {
  const ativas = todasAssinaturas.filter(a => a.status === 'ativa');
  const total = ativas.reduce((acc, a) => acc + a.valor_mensal, 0);
  document.getElementById('total-mensal').textContent = formatarMoeda(total);
}

function renderizarRenovacoes() {
  const container = document.getElementById('renovacoes-list');
  const proximas = todasAssinaturas
    .filter(a => a.status === 'ativa' && diasAteRenovacao(a.data_renovacao) >= 0)
    .sort((a, b) => diasAteRenovacao(a.data_renovacao) - diasAteRenovacao(b.data_renovacao))
    .slice(0, 4);

  if (proximas.length === 0) {
    container.innerHTML = '<div class="empty">Nenhuma renovação próxima.</div>';
    return;
  }

  container.innerHTML = proximas.map(a => {
    const dias = diasAteRenovacao(a.data_renovacao);
    const label = dias === 0 ? 'Renova hoje' : dias === 1 ? 'Renova amanhã' : `Renova em ${dias} dias`;
    return `
      <div class="renewal-item">
        <div class="service-logo">
          <img src="${logoUrl(a.nome_servico)}" alt="${a.nome_servico}"
            onerror="this.style.display='none';this.parentElement.textContent='${a.nome_servico[0]}'" />
        </div>
        <div class="renewal-info">
          <div class="renewal-name">${a.nome_servico}</div>
          <div class="renewal-days">${label}</div>
        </div>
        <div class="renewal-value">${formatarMoeda(a.valor_mensal)}</div>
      </div>`;
  }).join('');
}

function aplicarFiltro() {
  renderizarAssinaturas();
}

function renderizarAssinaturas() {
  const container = document.getElementById('assinaturas-list');
  const filtro = document.getElementById('filtro-status').value;
  let lista = filtro === 'todas' ? todasAssinaturas : todasAssinaturas.filter(a => a.status === filtro);

  if (lista.length === 0) {
    container.innerHTML = '<div class="empty">Nenhuma assinatura encontrada.</div>';
    return;
  }

  container.innerHTML = lista.map(a => `
    <div class="sub-item">
      <div class="service-logo">
        <img src="${logoUrl(a.nome_servico)}" alt="${a.nome_servico}"
          onerror="this.style.display='none';this.parentElement.textContent='${a.nome_servico[0]}'" />
      </div>
      <div class="sub-info">
        <div class="sub-name">${a.nome_servico}</div>
        <div class="sub-category">${a.tipo_plano || 'Sem plano'}</div>
      </div>
      <div class="sub-value">${formatarMoeda(a.valor_mensal)}</div>
      <div class="sub-actions">
        <button class="btn-icon" title="Editar" onclick="abrirModalEditar(${a.id_assinatura})">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
        </button>
        <button class="btn-icon danger" title="Excluir" onclick="excluirAssinatura(${a.id_assinatura})">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg>
        </button>
      </div>
    </div>`).join('');
}

async function carregarCategorias() {
  try {
    const res = await fetch(`${API}/categorias`);
    const categorias = await res.json();
    const select = document.getElementById('input-categoria');
    select.innerHTML = categorias.map(c =>
      `<option value="${c.id_categoria}">${c.nome_categoria}</option>`
    ).join('');
  } catch {
    console.error('Erro ao carregar categorias');
  }
}

function abrirModal() {
  editandoId = null;
  document.getElementById('modal-title').textContent = 'Nova assinatura';
  document.getElementById('input-nome').value = '';
  document.getElementById('input-valor').value = '';
  document.getElementById('input-renovacao').value = '';
  document.getElementById('input-plano').value = '';
  document.getElementById('modal').classList.add('open');
  carregarCategorias();
}

function abrirModalEditar(id) {
  const a = todasAssinaturas.find(x => x.id_assinatura === id);
  if (!a) return;
  editandoId = id;
  document.getElementById('modal-title').textContent = 'Editar assinatura';
  document.getElementById('input-nome').value = a.nome_servico;
  document.getElementById('input-valor').value = a.valor_mensal;
  document.getElementById('input-renovacao').value = a.data_renovacao;
  document.getElementById('input-plano').value = a.tipo_plano || '';
  document.getElementById('modal').classList.add('open');
  carregarCategorias().then(() => {
    document.getElementById('input-categoria').value = a.id_categoria;
  });
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
    data_renovacao: document.getElementById('input-renovacao').value,
    tipo_plano: document.getElementById('input-plano').value,
    id_categoria: parseInt(document.getElementById('input-categoria').value),
    id_usuario: getIdUsuario(),
    status: 'ativa'
  };

  if (!dados.nome_servico || !dados.valor_mensal || !dados.data_renovacao) {
    alert('Preencha os campos obrigatórios.');
    return;
  }

  try {
    const url = editandoId ? `${API}/assinaturas/${editandoId}` : `${API}/assinaturas`;
    const method = editandoId ? 'PUT' : 'POST';
    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(dados)
    });

    if (res.ok) {
      fecharModal();
      carregarAssinaturas();
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
    const res = await fetch(`${API}/assinaturas/${id}`, { method: 'DELETE' });
    if (res.ok) carregarAssinaturas();
    else alert('Erro ao excluir.');
  } catch {
    alert('Erro de conexão com a API.');
  }
}

async function init() {
  await carregarUsuariosSelect();
  carregarAssinaturas();
}

init();
