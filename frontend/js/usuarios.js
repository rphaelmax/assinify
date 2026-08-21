let editandoId = null;
let usuarioAtual = null;

async function carregarUsuarios() {
  try {
    const res = await apiFetch('/usuarios');
    const usuarios = await res.json();
    renderizarTabela(usuarios);
  } catch {
    document.getElementById('tbody').innerHTML = '<tr><td colspan="5" class="empty">Erro ao carregar usuários.</td></tr>';
  }
}

function renderizarTabela(usuarios) {
  const tbody = document.getElementById('tbody');
  if (usuarios.length === 0) {
    tbody.innerHTML = '<tr><td colspan="5" class="empty">Nenhum usuário cadastrado.</td></tr>';
    return;
  }
  tbody.innerHTML = usuarios.map(u => {
    const ehVoceMesmo = usuarioAtual && u.id_usuario === usuarioAtual.id_usuario;
    const proximaRole = u.role === 'admin' ? 'user' : 'admin';
    const tituloPromover = u.role === 'admin' ? 'Remover permissão de admin' : 'Tornar admin';

    return `
    <tr>
      <td>${u.id_usuario}</td>
      <td><strong>${u.nome}</strong>${ehVoceMesmo ? ' <span style="color:var(--text-muted);font-weight:400;">(você)</span>' : ''}</td>
      <td>${u.email}</td>
      <td><span class="role-badge role-badge-${u.role}">${u.role === 'admin' ? 'Admin' : 'Usuário'}</span></td>
      <td>
        <div style="display:flex;gap:6px;">
          <button class="btn-icon" title="Editar" onclick="abrirModalEditar(${u.id_usuario}, '${u.nome}', '${u.email}')">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
          </button>
          ${!ehVoceMesmo ? `
          <button class="btn-icon" title="${tituloPromover}" onclick="alternarRole(${u.id_usuario}, '${proximaRole}')">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2 2 7l10 5 10-5-10-5Z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>
          </button>
          <button class="btn-icon danger" title="Excluir" onclick="excluir(${u.id_usuario})">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg>
          </button>` : ''}
        </div>
      </td>
    </tr>`;
  }).join('');
}

function abrirModalEditar(id, nome, email) {
  editandoId = id;
  document.getElementById('modal-title').textContent = 'Editar usuário';
  document.getElementById('input-nome').value = nome;
  document.getElementById('input-email').value = email;
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
    email: document.getElementById('input-email').value
  };

  if (!dados.nome || !dados.email) {
    alert('Nome e e-mail são obrigatórios.');
    return;
  }

  try {
    const res = await apiFetch(`/usuarios/${editandoId}`, { method: 'PUT', body: JSON.stringify(dados) });

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

async function alternarRole(id, novaRole) {
  const acao = novaRole === 'admin' ? 'tornar este usuário admin' : 'remover a permissão de admin deste usuário';
  if (!confirm(`Tem certeza que deseja ${acao}?`)) return;

  try {
    const res = await apiFetch(`/usuarios/${id}/role`, { method: 'PATCH', body: JSON.stringify({ role: novaRole }) });
    if (res.ok) carregarUsuarios();
    else {
      const err = await res.json();
      alert(err.erro || 'Erro ao alterar permissão.');
    }
  } catch {
    alert('Erro de conexão com a API.');
  }
}

async function excluir(id) {
  if (!confirm('Deseja excluir este usuário?')) return;
  try {
    const res = await apiFetch(`/usuarios/${id}`, { method: 'DELETE' });
    if (res.ok) carregarUsuarios();
    else alert('Erro ao excluir.');
  } catch {
    alert('Erro de conexão com a API.');
  }
}

async function init() {
  usuarioAtual = await protegerPagina();
  if (!usuarioAtual) return;
  if (!exigirAdmin(usuarioAtual)) return;
  carregarUsuarios();
}

init();
