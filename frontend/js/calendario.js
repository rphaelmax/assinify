let calAno, calMes;
let calRenovacoes = [];   // renovações do mês exibido, vindas de /assinaturas/calendario
let calRequisicao = 0;
let calErro = null;       // mensagem quando a API falha (em vez de mostrar calendário vazio)    // descarta respostas antigas quando o usuário navega rápido

const MESES_PT = ['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro'];
const DIAS_SEMANA = ['Dom','Seg','Ter','Qua','Qui','Sex','Sáb'];
const CAL_STORAGE_KEY = 'assinify_cal_expandido';

function initCalendario() {
  const hoje = new Date();
  calAno = hoje.getFullYear();
  calMes = hoje.getMonth();
}

function isCalendarioExpandido() {
  // padrão: expandido; só fica recolhido se o usuário recolheu
  try { return localStorage.getItem(CAL_STORAGE_KEY) !== '0'; } catch { return true; }
}

function toggleCalendario() {
  const card = document.getElementById('card-calendario');
  if (!card) return;
  const expandir = !card.classList.contains('cal-expandido');
  card.classList.toggle('cal-expandido', expandir);
  const btn = document.getElementById('btn-cal-toggle');
  if (btn) {
    btn.setAttribute('aria-expanded', String(expandir));
    btn.title = expandir ? 'Recolher calendário' : 'Expandir calendário';
  }
  try { localStorage.setItem(CAL_STORAGE_KEY, expandir ? '1' : '0'); } catch {}
}

function calendarioAnterior() {
  calMes--;
  if (calMes < 0) { calMes = 11; calAno--; }
  renderizarCalendario();
}

function calendarioProximo() {
  calMes++;
  if (calMes > 11) { calMes = 0; calAno++; }
  renderizarCalendario();
}

function assinaturasNoDia(dia) {
  return calRenovacoes.filter(r => r.dia === dia);
}

// Retorna false se a resposta ficou obsoleta (outra navegação começou depois).
async function carregarCalendario() {
  const requisicao = ++calRequisicao;
  let renovacoes = [];
  let erro = null;
  try {
    const res = await apiFetch(`/assinaturas/calendario?ano=${calAno}&mes=${calMes + 1}`);
    if (res.ok) renovacoes = (await res.json()).renovacoes || [];
    else erro = `Não foi possível carregar o calendário (erro ${res.status}). Reinicie a API.`;
  } catch {
    erro = 'Não foi possível carregar o calendário. Verifique se a API está rodando.';
  }
  if (requisicao !== calRequisicao) return false;
  calRenovacoes = renovacoes;
  calErro = erro;
  return true;
}

async function renderizarCalendario() {
  if (typeof calAno === 'undefined') initCalendario();
  const card = document.getElementById('card-calendario');
  const grid = document.getElementById('calendario-grid');
  const titulo = document.getElementById('cal-mes-ano');
  if (!card || !grid) return;

  card.style.display = '';
  // Restaura estado recolhido/expandido sem sobrescrever escolha do usuário
  const expandido = isCalendarioExpandido();
  card.classList.toggle('cal-expandido', expandido);
  const btn = document.getElementById('btn-cal-toggle');
  if (btn) {
    btn.setAttribute('aria-expanded', String(expandido));
    btn.title = expandido ? 'Recolher calendário' : 'Expandir calendário';
  }
  titulo.textContent = `${MESES_PT[calMes]} ${calAno}`;

  if (!(await carregarCalendario())) return;
  desenharCalendario();
}

function desenharCalendario() {
  const grid = document.getElementById('calendario-grid');
  const legenda = document.getElementById('calendario-legenda');
  const resumo = document.getElementById('cal-resumo');

  const diasNoMes = new Date(calAno, calMes + 1, 0).getDate();
  const primeiroDiaSemana = new Date(calAno, calMes, 1).getDay();
  const hoje = new Date(); hoje.setHours(0,0,0,0);
  const ehMesAtual = hoje.getFullYear() === calAno && hoje.getMonth() === calMes;

  // Resumo sempre visível, mesmo recolhido
  if (resumo) {
    if (calErro) {
      resumo.innerHTML = `<span class="cal-resumo-vazio">${escapar(calErro)}</span>`;
    } else if (calRenovacoes.length === 0) {
      resumo.innerHTML = '<span class="cal-resumo-vazio">Nenhuma renovação neste mês.</span>';
    } else {
      const proximas = calRenovacoes.slice(0, 3).map(r => `${r.dia} · ${escapar(r.nome_servico)}`).join(' · ');
      const resto = calRenovacoes.length > 3 ? ` <span class="cal-resumo-mais">+${calRenovacoes.length - 3} neste mês</span>` : '';
      resumo.innerHTML = `<span class="cal-resumo-dots"><span class="cal-dot"></span> ${calRenovacoes.length} renovação(ões) em ${MESES_PT[calMes]}</span><span class="cal-resumo-lista">${proximas}${resto}</span>`;
    }
  }

  let html = '<div class="cal-grid">';
  for (const d of DIAS_SEMANA) html += `<div class="cal-head">${d}</div>`;
  for (let i = 0; i < primeiroDiaSemana; i++) html += '<div class="cal-day cal-day--empty"></div>';
  for (let dia = 1; dia <= diasNoMes; dia++) {
    const lista = assinaturasNoDia(dia);
    const isHoje = ehMesAtual && hoje.getDate() === dia;
    const temEvento = lista.length > 0;
    const cls = `cal-day${temEvento ? ' cal-day--has-event' : ''}${isHoje ? ' cal-day--hoje' : ''}`;
    const title = temEvento ? lista.map(a => a.nome_servico).join(', ') : '';
    const dots = temEvento ? `<div class="cal-dots">${lista.slice(0,3).map(() => '<span class="cal-dot"></span>').join('')}${lista.length > 3 ? `<span class="cal-more">+${lista.length - 3}</span>` : ''}</div>` : '';
    const tooltip = temEvento ? ` title="${escapar(title)}"` : '';
    html += `<div class="${cls}"${tooltip} onclick="mostrarDiaCalendario(${dia})"><span class="cal-num">${dia}</span>${dots}</div>`;
  }
  html += '</div>';
  grid.innerHTML = html;

  if (legenda) {
    const servicos = new Set(calRenovacoes.map(r => r.id_assinatura)).size;
    legenda.innerHTML = servicos ? `<span class="cal-legenda-dot"></span> ${servicos} assinatura(s) com renovação neste mês` : '';
  }
}

function mostrarDiaCalendario(dia) {
  const lista = assinaturasNoDia(dia);
  if (!lista.length) return;
  const nomes = lista.map(a => `• ${a.nome_servico} — ${formatarMoeda(a.valor_mensal)} (${a.periodicidade || 'mensal'})`).join('\n');
  alert(`${dia} de ${MESES_PT[calMes]}:\n${nomes}`);
}