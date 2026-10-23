/**
 * Utilitário compartilhado de força de senha.
 * Usado em registro.html e perfil.html (nova senha).
 * Sem dependências. Mantém paridade com backend/app/validacao.py:validar_forca_senha
 */

function calcularForcaSenha(senha) {
  if (!senha) return { score: 0, nivel: 0 };
  let score = 0;
  if (senha.length >= 6) score++;
  if (senha.length >= 10) score++;
  const temMaiuscula = /[A-Z]/.test(senha);
  const temMinuscula = /[a-z]/.test(senha);
  const temDigito = /\d/.test(senha);
  const temSimbolo = /[^A-Za-z0-9]/.test(senha);
  if (temMaiuscula && temMinuscula) score++;
  if (temDigito) score++;
  if (temSimbolo) score++;
  if (/^(.)\1+$/.test(senha) || /^(123|abc|qwerty)/i.test(senha)) score = Math.min(score, 1);
  const tipos = Number(temMaiuscula || temMinuscula) + Number(temDigito) + Number(temSimbolo);
  if (tipos <= 1 && !(temMaiuscula && temMinuscula)) score = Math.min(score, 0);
  const nivel = Math.min(score, 4);
  return { score, nivel };
}

const NIVEIS_FORCA = [
  { w: '20%', c: '#EF4444', t: 'Muito fraca' },
  { w: '40%', c: '#F59E0B', t: 'Fraca' },
  { w: '60%', c: '#F59E0B', t: 'Razoável' },
  { w: '80%', c: '#10B981', t: 'Forte' },
  { w: '100%', c: '#059669', t: 'Muito forte' },
];

function renderizarForcaSenha(inputId, fillId, textId, wrapperId) {
  const senha = (document.getElementById(inputId)?.value) || '';
  const fill = document.getElementById(fillId);
  const text = document.getElementById(textId);
  const wrapper = document.getElementById(wrapperId);
  if (!fill || !text || !wrapper) return 0;

  if (!senha) {
    wrapper.style.display = 'none';
    fill.style.width = '0';
    text.textContent = '';
    return 0;
  }
  wrapper.style.display = '';
  const { nivel } = calcularForcaSenha(senha);
  const n = NIVEIS_FORCA[nivel] || NIVEIS_FORCA[0];
  fill.style.width = n.w;
  fill.style.background = n.c;
  text.textContent = n.t;
  text.style.color = n.c;
  return nivel;
}

function senhaEhForteSuficiente(senha, minimoNivel = 1) {
  const { nivel } = calcularForcaSenha(senha);
  return nivel >= minimoNivel;
}