const API = 'http://localhost:5000';
const TOKEN_KEY = 'assinify_token';
const ROLE_KEY = 'assinify_role'; // cache da role só para o menu não piscar; a API continua sendo a fonte da verdade
const LOGO_TOKEN = 'pk_aFebUAI6TXi3KllA2BUauA';

// Gera a URL do logo da empresa usando o domínio baseado no primeiro nome do serviço
// e a API do logo.dev.
function logoUrl(nome) {
  const limpo = nome.toLowerCase()
    .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9\s]/g, '')
    .trim()
    .split(/\s+/)[0];
  return `https://img.logo.dev/${limpo}.com?token=${LOGO_TOKEN}&format=webp&retina=true`;
}

function escapar(valor) {
  return String(valor ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

document.addEventListener('error', (e) => {
  const img = e.target;
  if (img.tagName === 'IMG' && img.dataset.inicial !== undefined) {
    img.parentElement.textContent = img.dataset.inicial;
  }
}, true);

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function salvarToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.removeItem(ROLE_KEY); // novo login: descarta a role do usuário anterior
}

function limparSessao() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(ROLE_KEY);
}

/** Mostra o item "Usuários" só para admin. No HTML ele nasce oculto (display:none). */
function aplicarMenuAdmin(role) {
  const navUsuarios = document.getElementById('nav-usuarios');
  if (navUsuarios) navUsuarios.style.display = role === 'admin' ? '' : 'none';
}

// Aplica já no carregamento usando a role em cache (evita o item aparecer/sumir ao trocar de aba)
try { aplicarMenuAdmin(localStorage.getItem(ROLE_KEY)); } catch { }

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
  // FormData (upload) define o próprio Content-Type, com o boundary
  if (options.body && !(options.body instanceof FormData) && !headers['Content-Type']) {
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

/**
 * Preenche um avatar: foto, se o usuário tiver, ou a inicial do nome.
 * Se a imagem falhar ao carregar, o listener global de 'error' (acima)
 * volta para a inicial via data-inicial.
 */
function renderizarAvatar(el, usuario) {
  if (!el) return;
  const inicial = usuario.nome[0].toUpperCase();
  el.textContent = '';
  if (!usuario.foto_url) {
    el.textContent = inicial;
    return;
  }
  const img = document.createElement('img');
  img.alt = '';
  img.dataset.inicial = inicial;
  img.src = `${API}${usuario.foto_url}`;
  el.appendChild(img);
}

// ── Moedas ───────────────────────────────────────────────────────
const MOEDAS_NOMES = {
  BRL: 'Real brasileiro', USD: 'Dólar americano', EUR: 'Euro', GBP: 'Libra esterlina',
  CAD: 'Dólar canadense', AUD: 'Dólar australiano', JPY: 'Iene japonês', CHF: 'Franco suíço',
  ARS: 'Peso argentino', MXN: 'Peso mexicano'
};
let moedaBase = 'BRL';

function definirMoedaBase(codigo) {
  if (MOEDAS_NOMES[codigo]) moedaBase = codigo;
}

/** Formata um valor na moeda informada (ou na moeda base do usuário). */
function formatarMoeda(valor, moeda) {
  return (valor || 0).toLocaleString('pt-BR', { style: 'currency', currency: moeda || moedaBase });
}

function opcoesMoeda(selecionada) {
  return Object.entries(MOEDAS_NOMES)
    .map(([codigo, nome]) => `<option value="${codigo}"${codigo === selecionada ? ' selected' : ''}>${codigo} · ${nome}</option>`)
    .join('');
}

function popularSidebar(usuario) {
  const avatar = document.getElementById('sidebar-avatar');
  const nome = document.getElementById('sidebar-nome');
  renderizarAvatar(avatar, usuario);
  definirMoedaBase(usuario.moeda_base);
  if (nome) nome.textContent = usuario.nome;

  // O item de menu "Usuários" só faz sentido pra quem administra a plataforma
  aplicarMenuAdmin(usuario.role);
  try { localStorage.setItem(ROLE_KEY, usuario.role); } catch { }
}

/** Bloqueia o acesso a uma página restrita a admin, redirecionando não-admins */
function exigirAdmin(usuario) {
  if (usuario.role !== 'admin') {
    window.location.href = 'dashboard.html';
    return false;
  }
  return true;
}