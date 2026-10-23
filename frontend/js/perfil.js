let usuarioAtual = null;

function mostrarFeedback(id, mensagem, tipo) {
  const el = document.getElementById(id);
  el.textContent = mensagem;
  el.className = 'form-feedback ' + (tipo === 'erro' ? 'form-feedback-erro' : 'form-feedback-sucesso');
  el.style.display = 'block';
  setTimeout(() => { el.style.display = 'none'; }, 4000);
}

function atualizarForcaSenha() {
  renderizarForcaSenha('senha-nova', 'senha-forca-fill', 'senha-forca-text', 'senha-forca');
}

async function salvarPerfil() {
  const nome = document.getElementById('perfil-nome').value.trim();
  const email = document.getElementById('perfil-email').value.trim();

  if (!nome || !email) {
    mostrarFeedback('perfil-feedback', 'Preencha nome e e-mail.', 'erro');
    return;
  }

  try {
    const res = await apiFetch('/auth/perfil', {
      method: 'PUT',
      body: JSON.stringify({ nome, email })
    });
    const dados = await res.json();
    if (!res.ok) {
      mostrarFeedback('perfil-feedback', dados.erro || 'Erro ao salvar.', 'erro');
      return;
    }
    usuarioAtual = dados;
    popularPerfil(dados);
    popularSidebar(dados);
    mostrarFeedback('perfil-feedback', 'Perfil atualizado com sucesso!', 'sucesso');
  } catch {
    mostrarFeedback('perfil-feedback', 'Erro de conexão com a API.', 'erro');
  }
}

async function alterarSenha() {
  const senhaAtual = document.getElementById('senha-atual').value;
  const novaSenha = document.getElementById('senha-nova').value;
  const confirmar = document.getElementById('senha-confirmar').value;

  if (!senhaAtual || !novaSenha) {
    mostrarFeedback('senha-feedback', 'Preencha todos os campos de senha.', 'erro');
    return;
  }
  if (novaSenha.length < 6) {
    mostrarFeedback('senha-feedback', 'A nova senha deve ter ao menos 6 caracteres.', 'erro');
    return;
  }
  if (novaSenha !== confirmar) {
    mostrarFeedback('senha-feedback', 'As senhas não coincidem.', 'erro');
    return;
  }

  try {
    const res = await apiFetch('/auth/senha', {
      method: 'PATCH',
      body: JSON.stringify({ senha_atual: senhaAtual, nova_senha: novaSenha })
    });
    const dados = await res.json();
    if (!res.ok) {
      mostrarFeedback('senha-feedback', dados.erro || 'Erro ao alterar senha.', 'erro');
      return;
    }
    document.getElementById('senha-atual').value = '';
    document.getElementById('senha-nova').value = '';
    document.getElementById('senha-confirmar').value = '';
    document.getElementById('senha-forca').style.display = 'none';
    mostrarFeedback('senha-feedback', 'Senha alterada com sucesso!', 'sucesso');
  } catch {
    mostrarFeedback('senha-feedback', 'Erro de conexão com a API.', 'erro');
  }
}

function popularPerfil(usuario) {
  document.getElementById('profile-avatar').textContent = usuario.nome[0].toUpperCase();
  document.getElementById('profile-nome').textContent = usuario.nome;
  document.getElementById('profile-email').textContent = usuario.email;
  const badge = document.getElementById('profile-role');
  badge.textContent = usuario.role === 'admin' ? 'Admin' : 'Usuário';
  badge.className = 'role-badge ' + (usuario.role === 'admin' ? 'role-badge-admin' : 'role-badge-user');

  document.getElementById('perfil-nome').value = usuario.nome;
  document.getElementById('perfil-email').value = usuario.email;
}

async function init() {
  usuarioAtual = await protegerPagina();
  if (!usuarioAtual) return;
  popularPerfil(usuarioAtual);
}

init();