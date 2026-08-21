const API = 'http://localhost:5000';
const TOKEN_KEY = 'assinify_token';
const LOGO_TOKEN = 'pk_aFebUAI6TXi3KllA2BUauA';

function logoUrl(nome) {
  const limpo = nome.toLowerCase()
    .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9\s]/g, '')
    .trim()
    .split(/\s+/)[0];
  return `https://img.logo.dev/${limpo}.com?token=${LOGO_TOKEN}&format=webp&retina=true`;
}

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function salvarToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

function limparSessao() {
  localStorage.removeItem(TOKEN_KEY);
}

function logout() {
  limparSessao();
  window.location.href = 'login.html';
}

/**
 * Wrapper de fetch que injeta o header Authorization automaticamente e
 * redireciona para o login se o token estiver ausente, expirado ou inválido.
 */
async function apiFetch(path, options = {}) {
  const token = getToken();
  const headers = { ...(options.headers || {}) };

  if (token) headers['Authorization'] = `Bearer ${token}`;
  if (options.body && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }

  const res = await fetch(`${API}${path}`, { ...options, headers });

  if (res.status === 401) {
    limparSessao();
    window.location.href = 'login.html';
    throw new Error('Sessão expirada');
  }

  return res;
}

/**
 * Garante que existe uma sessão válida nesta página, busca o usuário
 * autenticado (via /auth/me) e popula o rodapé da sidebar. Chame no
 * carregamento de toda página protegida. Retorna o usuário autenticado.
 */
async function protegerPagina() {
  if (!getToken()) {
    window.location.href = 'login.html';
    return null;
  }

  const res = await apiFetch('/auth/me');
  if (!res.ok) return null;

  const usuario = await res.json();
  popularSidebar(usuario);
  return usuario;
}

function popularSidebar(usuario) {
  const avatar = document.getElementById('sidebar-avatar');
  const nome = document.getElementById('sidebar-nome');
  if (avatar) avatar.textContent = usuario.nome[0].toUpperCase();
  if (nome) nome.textContent = usuario.nome;

  // O item de menu "Usuários" só faz sentido pra quem administra a plataforma
  const navUsuarios = document.getElementById('nav-usuarios');
  if (navUsuarios && usuario.role !== 'admin') {
    navUsuarios.remove();
  }
}

/** Bloqueia o acesso a uma página restrita a admin, redirecionando não-admins. */
function exigirAdmin(usuario) {
  if (usuario.role !== 'admin') {
    window.location.href = 'dashboard.html';
    return false;
  }
  return true;
}