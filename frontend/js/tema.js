const TEMA_KEY = 'assinify_tema'; // 'light' | 'dark' | 'auto'

function temaEfetivo(valor) {
  if (valor === 'dark') return 'dark';
  if (valor === 'light') return 'light';
  // auto: segue o sistema
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

function aplicarTema(valor) {
  const efetivo = temaEfetivo(valor);
  document.documentElement.setAttribute('data-theme', efetivo);
  const meta = document.querySelector('meta[name="theme-color"]');
  if (meta) meta.content = efetivo === 'dark' ? '#0B1120' : '#F8FAFC';
  atualizarIconeTema(valor);
  document.dispatchEvent(new CustomEvent('temachange', { detail: efetivo }));
}

function obterTemaSalvo() {
  try { return localStorage.getItem(TEMA_KEY) || 'auto'; } catch { return 'auto'; }
}

function salvarTema(valor) {
  try { localStorage.setItem(TEMA_KEY, valor); } catch {}
}

function atualizarIconeTema(valor) {
  const btn = document.getElementById('btn-tema');
  if (!btn) return;
  const efetivo = temaEfetivo(valor);
  btn.setAttribute('aria-label', efetivo === 'dark' ? 'Mudar para modo claro' : 'Mudar para modo escuro');
  btn.title = efetivo === 'dark' ? 'Modo claro' : 'Modo escuro';
  // troca ícone via classe
  btn.dataset.theme = efetivo;
}

function alternarTema() {
  const atual = obterTemaSalvo();
  // ciclo: auto -> light -> dark -> auto (mas UX simples: alterna efetivo)
  const efetivo = temaEfetivo(atual);
  const proximo = efetivo === 'dark' ? 'light' : 'dark';
  salvarTema(proximo);
  aplicarTema(proximo);
}

// Aplica o mais cedo possível (evita flash)
(function initTemaSync() {
  try {
    const salvo = obterTemaSalvo();
    const efetivo = temaEfetivo(salvo);
    document.documentElement.setAttribute('data-theme', efetivo);
  } catch {}
})();

// Reage a mudança do sistema quando em 'auto'
try {
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    if (obterTemaSalvo() === 'auto') aplicarTema('auto');
  });
} catch {}

// Quando o DOM estiver pronto, garante ícone correto
document.addEventListener('DOMContentLoaded', () => aplicarTema(obterTemaSalvo()));