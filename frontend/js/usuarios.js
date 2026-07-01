const API = 'http://localhost:5000';
let editandoId = null;

async function carregarUsuarios() {
  try {
    const res = await fetch(`${API}/usuarios`);
    const usuarios = await res.json();
    renderizarTabela(usuarios);
  } catch {
    document.getElementById('tbody').innerHTML = '<tr><td colspan="4" class="empty">Erro ao carregar usuários.</td></tr>';
  }
}

function renderizarTabela(usuarios) {
  const tbody = document.getElementById('tbody');
  if (usuarios.length === 0) {
    tbody.innerHTML = '<tr><td colspan="4" class="empty">Nenhum usuário cadastrado.</td></tr>';
    return;
  }
  tbody.innerHTML = usuarios.map(u => `
    <tr>
      <td>${u.id_usuario}</td>
      <td><strong>${u.nome}</strong></td>
      <td>${u.email}</td>
      <td>${u.telefone || '—'}</td>
      <td>
        <div style="display:flex;gap:6px;">
          <button class="btn-icon" title="Editar" onclick="abrirModalEditar(${u.id_usuario}, '${u.nome}', '${u.email}', '${u.telefone || ''}')">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
          </button>
          <button class="btn-icon danger" title="Excluir" onclick="excluir(${u.id_usuario})">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg>
          </button>
        </div>
      </td>
    </tr>`).join('');
}

function abrirModal() {
  editandoId = null;
  document.getElementById('modal-title').textContent = 'Novo usuário';
  document.getElementById('input-nome').value = '';
  document.getElementById('input-email').value = '';
  document.getElementById('input-senha').value = '';
  document.getElementById('input-telefone').value = '';
  document.getElementById('modal').classList.add('open');
}

function abrirModalEditar(id, nome, email, telefone) {
  editandoId = id;
  document.getElementById('modal-title').textContent = 'Editar usuário';
  document.getElementById('input-nome').value = nome;
  document.getElementById('input-email').value = email;
  document.getElementById('input-senha').value = '';
  document.getElementById('input-telefone').value = telefone;
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
    nome: document.getElementById('input-nome').value,
    email: document.getElementById('input-email').value,
    senha: document.getElementById('input-senha').value,
    telefone: document.getElementById('input-telefone').value
  };

  if (!dados.nome || !dados.email) {
    alert('Nome e e-mail são obrigatórios.');
    return;
  }
  if (!editandoId && !dados.senha) {
    alert('Senha é obrigatória.');
    return;
  }

  try {
    const url = editandoId ? `${API}/usuarios/${editandoId}` : `${API}/usuarios`;
    const method = editandoId ? 'PUT' : 'POST';
    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(dados)
    });

    if (res.ok) {
      fecharModal();
      carregarUsuarios();
    } else {
      const err = await res.json();
      alert(err.erro || 'Erro ao salvar.');
    }
  } catch {
    alert('Erro de conexão com a API.');
  }
}

async function excluir(id) {
  if (!confirm('Deseja excluir este usuário?')) return;
  try {
    const res = await fetch(`${API}/usuarios/${id}`, { method: 'DELETE' });
    if (res.ok) carregarUsuarios();
    else alert('Erro ao excluir.');
  } catch {
    alert('Erro de conexão com a API.');
  }
}

carregarUsuarios();
