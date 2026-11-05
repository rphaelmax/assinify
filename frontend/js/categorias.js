let editandoId = null;
let usuarioAtual = null;
let listaCategorias = [];

async function carregarCategorias() {
  try {
    const res = await apiFetch('/categorias');
    listaCategorias = await res.json();
    renderizarTabela(listaCategorias);
  } catch {
    document.getElementById('tbody').innerHTML = '<tr><td colspan="3" class="empty">Erro ao carregar categorias.</td></tr>';
  }
}

function renderizarTabela(categorias) {
  const tbody = document.getElementById('tbody');

  if (categorias.length === 0) {
    tbody.innerHTML = '<tr><td colspan="3" class="empty">Nenhuma categoria cadastrada.</td></tr>';
    return;
  }
  tbody.innerHTML = categorias.map(c => `
    <tr>
      <td data-label="Nome"><strong>${escapar(c.nome_categoria)}</strong></td>
      <td data-label="Descrição">${escapar(c.descricao || '—')}</td>
      <td data-label="Ações">
        <div style="display:flex;gap:6px;">
          <button class="btn-icon" title="Editar" onclick="abrirModalEditar(${c.id_categoria})">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
          </button>
          <button class="btn-icon danger" title="Excluir" onclick="excluir(${c.id_categoria})">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg>
          </button>
        </div>
      </td>
    </tr>`).join('');
}

function abrirModal() {
  editandoId = null;
  document.getElementById('modal-title').textContent = 'Nova categoria';
  document.getElementById('input-nome').value = '';
  document.getElementById('input-descricao').value = '';
  UI.limparErroForm('modal-erro');
  document.getElementById('modal').classList.add('open');
}

function abrirModalEditar(id) {
  const c = listaCategorias.find(x => x.id_categoria === id);
  if (!c) return;
  editandoId = id;
  document.getElementById('modal-title').textContent = 'Editar categoria';
  document.getElementById('input-nome').value = c.nome_categoria;
  document.getElementById('input-descricao').value = c.descricao || '';
  UI.limparErroForm('modal-erro');
  document.getElementById('modal').classList.add('open');
}

function fecharModal() {
  document.getElementById('modal').classList.remove('open');
}

function fecharModalFora(e) {
  if (e.target === document.getElementById('modal')) fecharModal();
}

async function salvar() {
  const dados = {
    nome_categoria: document.getElementById('input-nome').value,
    descricao: document.getElementById('input-descricao').value
  };

  if (!dados.nome_categoria) {
    UI.erroForm('modal-erro', 'Nome da categoria é obrigatório.');
    return;
  }

  try {
    const url = editandoId ? `/categorias/${editandoId}` : '/categorias';
    const method = editandoId ? 'PUT' : 'POST';
    const res = await apiFetch(url, { method, body: JSON.stringify(dados) });

    if (res.ok) {
      fecharModal();
      UI.toast(editandoId ? 'Categoria atualizada.' : 'Categoria criada.', 'sucesso');
      carregarCategorias();
    } else {
      const err = await res.json();
      UI.erroForm('modal-erro', err.erro || 'Erro ao salvar.');
    }
  } catch {
    UI.erroForm('modal-erro', 'Erro de conexão com a API.');
  }
}

async function excluir(id) {
  const c = listaCategorias.find(x => x.id_categoria === id);
  const confirmado = await UI.confirmar({
    titulo: c ? `Excluir ${c.nome_categoria}?` : 'Excluir categoria?',
    mensagem: 'Essa ação não pode ser desfeita. Categorias que ainda têm assinaturas não podem ser excluídas.',
    textoConfirmar: 'Excluir',
    perigo: true
  });
  if (!confirmado) return;
  try {
    const res = await apiFetch(`/categorias/${id}`, { method: 'DELETE' });
    if (res.ok) {
      UI.toast('Categoria excluída.', 'sucesso');
      carregarCategorias();
    } else {
      const err = await res.json().catch(() => ({}));
      UI.toast(err.erro || 'Erro ao excluir.', 'erro');
    }
  } catch {
    UI.toast('Erro de conexão com a API.', 'erro');
  }
}

async function init() {
  usuarioAtual = await protegerPagina();
  if (!usuarioAtual) return;
  carregarCategorias();
}

init();