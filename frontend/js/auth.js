function mostrarErro(mensagem) {
  const el = document.getElementById('auth-error');
  el.textContent = mensagem;
  el.classList.add('show');
}

function limparErro() {
  document.getElementById('auth-error').classList.remove('show');
}

function definirCarregando(botao, carregando, textoOriginal) {
  botao.disabled = carregando;
  botao.textContent = carregando ? 'Aguarde...' : textoOriginal;
}

async function entrar(event) {
  event.preventDefault();
  limparErro();

  const botao = document.getElementById('btn-submit');
  const email = document.getElementById('input-email').value.trim();
  const senha = document.getElementById('input-senha').value;

  if (!email || !senha) {
    mostrarErro('Preencha email e senha.');
    return;
  }

  definirCarregando(botao, true, 'Entrar');
  try {
    const res = await fetch(`${API}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, senha })
    });
    const dados = await res.json();

    if (!res.ok) {
      mostrarErro(dados.erro || 'Não foi possível entrar.');
      return;
    }

    salvarToken(dados.token);
    window.location.href = 'dashboard.html';
  } catch {
    mostrarErro('Erro de conexão com a API.');
  } finally {
    definirCarregando(botao, false, 'Entrar');
  }
}

async function registrar(event) {
  event.preventDefault();
  limparErro();

  const botao = document.getElementById('btn-submit');
  const nome = document.getElementById('input-nome').value.trim();
  const email = document.getElementById('input-email').value.trim();
  const senha = document.getElementById('input-senha').value;
  const confirmarSenha = document.getElementById('input-confirmar-senha').value;

  if (!nome || !email || !senha) {
    mostrarErro('Preencha todos os campos.');
    return;
  }
  if (senha.length < 6) {
    mostrarErro('A senha deve ter ao menos 6 caracteres.');
    return;
  }
  if (senha !== confirmarSenha) {
    mostrarErro('As senhas não coincidem.');
    return;
  }

  definirCarregando(botao, true, 'Criar conta');
  try {
    const res = await fetch(`${API}/auth/registrar`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ nome, email, senha })
    });
    const dados = await res.json();

    if (!res.ok) {
      mostrarErro(dados.erro || 'Não foi possível criar a conta.');
      return;
    }

    // Cadastro não retorna token — loga em seguida com as mesmas credenciais.
    const loginRes = await fetch(`${API}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, senha })
    });
    const loginDados = await loginRes.json();

    if (!loginRes.ok) {
      window.location.href = 'login.html';
      return;
    }

    salvarToken(loginDados.token);
    window.location.href = 'dashboard.html';
  } catch {
    mostrarErro('Erro de conexão com a API.');
  } finally {
    definirCarregando(botao, false, 'Criar conta');
  }
}

// Se já existe uma sessão, não faz sentido ver a tela de login/registro de novo.
if (getToken()) {
  window.location.href = 'dashboard.html';
}

// Usa o mesmo mecanismo do Logo.dev já usado no dashboard (logoUrl, em api.js)
// para os logos ilustrativos do preview card, em vez de uma implementação paralela.
document.querySelectorAll('.auth-preview-logo[data-nome]').forEach((el) => {
  const img = el.querySelector('img');
  if (img) img.src = logoUrl(el.dataset.nome);
});