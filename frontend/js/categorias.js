const API = 'http://localhost:5000';
let editandoId = null;

async function carregarCategorias() {
  try {
    const res = await fetch(`${API}/categorias`);
    const categorias = await res.json();
    renderizarTabela(categorias);
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
      <td>${c.id_categoria}</td>
      <td><strong>${c.nome_categoria}</strong></td>
      <td>${c.descricao || '—'}</td>
      <td>
        <div style="display:flex;gap:6px;">
          <button class="btn-icon" title="Editar" onclick="abrirModalEditar(${c.id_categoria}, '${c.nome_categoria}', '${c.descricao || ''}')">
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
  document.getElementById('modal').classList.add('open');
}

function abrirModalEditar(id, nome, descricao) {
  editandoId = id;
  document.getElementById('modal-title').textContent = 'Editar categoria';
  document.getElementById('input-nome').value = nome;
  document.getElementById('input-descricao').value = descricao;
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
    alert('Nome da categoria é obrigatório.');
    return;
  }

  try {
    const url = editandoId ? `${API}/categorias/${editandoId}` : `${API}/categorias`;
    const method = editandoId ? 'PUT' : 'POST';
    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(dados)
    });

    if (res.ok) {
      fecharModal();
      carregarCategorias();
    } else {
      const err = await res.json();
      alert(err.erro || 'Erro ao salvar.');
    }
  } catch {
    alert('Erro de conexão com a API.');
  }
}

async function excluir(id) {
  if (!confirm('Deseja excluir esta categoria?')) return;
  try {
    const res = await fetch(`${API}/categorias/${id}`, { method: 'DELETE' });
    if (res.ok) carregarCategorias();
    else alert('Erro ao excluir.');
  } catch {
    alert('Erro de conexão com a API.');
  }
}

carregarCategorias();
