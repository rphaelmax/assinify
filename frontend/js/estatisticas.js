let dados = null;
const graficos = {};

const PERIODICIDADE_LABEL = { semanal: 'Semanal', mensal: 'Mensal', anual: 'Anual' };

const METODOS_PAGAMENTO_LABEL = {
  cartao_credito: 'Cartão de crédito',
  cartao_debito: 'Cartão de débito',
  pix: 'PIX',
  boleto: 'Boleto',
  debito_automatico: 'Débito automático',
  transferencia: 'Transferência',
  outro: 'Outro'
};

const MESES_CURTOS = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
const MESES_LONGOS = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'];
const CORES = ['#2563EB', '#0EA5E9', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#6366F1', '#14B8A6', '#F97316'];

// Mês acima da média em pelo menos 25% passa a ser tratado como "pesado"
const LIMIAR_MES_PESADO = 1.25;

// ── Formatação ────────────────────────────────────────────────────
// Todos os valores desta página vêm convertidos para a moeda base do usuário.
function moeda(valor) {
  return formatarMoeda(valor);
}

function moedaCurta(valor) {
  return (valor || 0).toLocaleString('pt-BR', { style: 'currency', currency: moedaBase, maximumFractionDigits: 0 });
}

function dataBr(iso) {
  return iso ? iso.split('-').reverse().join('/') : '';
}

function percentual(valor) {
  return (valor || 0).toLocaleString('pt-BR', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + '%';
}

function plural(n, singular, pluralTxt) {
  return `${n} ${n === 1 ? singular : pluralTxt}`;
}

function forte(texto) {
  return `<strong>${escapar(texto)}</strong>`;
}

function nomeMes(m, comAno = false) {
  const base = MESES_LONGOS[m.mes - 1];
  const anoAtual = new Date().getFullYear();
  return comAno || m.ano !== anoAtual ? `${base} de ${m.ano}` : base;
}

function corCss(nome) {
  return getComputedStyle(document.documentElement).getPropertyValue(nome).trim();
}

function logoHtml(nome) {
  return `<div class="service-logo"><img src="${logoUrl(nome)}" alt="" data-inicial="${escapar(nome[0] || '?')}" /></div>`;
}

// ── Estados da página ────────────────────────────────────────────
function mostrar(estado) {
  const ids = { loading: 'est-loading', erro: 'est-erro', vazio: 'est-vazio', conteudo: 'est-conteudo' };
  Object.entries(ids).forEach(([chave, id]) => {
    document.getElementById(id).style.display = chave === estado ? '' : 'none';
  });
}

async function carregarEstatisticasDetalhadas() {
  const btn = document.getElementById('btn-atualizar');
  if (btn) btn.disabled = true;
  mostrar('loading');

  try {
    const res = await apiFetch('/assinaturas/estatisticas/detalhadas');
    if (!res.ok) throw new Error('Falha ao carregar estatísticas');
    dados = await res.json();
  } catch {
    dados = null;
    mostrar('erro');
    if (btn) btn.disabled = false;
    return;
  }

  if (btn) btn.disabled = false;

  definirMoedaBase(dados.moeda_base);

  if (!dados.resumo.ativas) {
    mostrar('vazio');
    return;
  }

  // O conteúdo precisa estar visível antes de desenhar os gráficos (Chart.js mede o canvas)
  mostrar('conteudo');
  renderizarTudo();
}

function renderizarTudo() {
  renderizarKpis(dados);
  renderizarDestaques(dados);
  renderizarProjecao(dados);
  renderizarJanelas(dados);
  renderizarRankingMaiores(dados);
  renderizarRankingCategorias(dados);
  renderizarGraficosPerfil(dados);
  renderizarReajustes(dados);
  renderizarCanceladas(dados);
}

// ── KPIs ──────────────────────────────────────────────────────────
const ICONES = {
  dinheiro: '<line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7H14a3.5 3.5 0 0 1 0 7H6"/>',
  calendario: '<rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>',
  ativas: '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>',
  media: '<path d="M3 3v18h18"/><path d="M18 17V9"/><path d="M13 17V5"/><path d="M8 17v-3"/>',
  maior: '<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>',
  economia: '<line x1="7" y1="7" x2="17" y2="17"/><polyline points="17 7 17 17 7 17"/>'
};

function cartaoKpi({ icone, cor, rotulo, valor, sub }) {
  return `
    <div class="stat-card">
      <div class="stat-icon stat-icon-${cor}">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">${ICONES[icone]}</svg>
      </div>
      <div>
        <div class="stat-label">${escapar(rotulo)}</div>
        <div class="stat-value" title="${escapar(valor)}">${escapar(valor)}</div>
        <div class="stat-sub" title="${escapar(sub)}">${escapar(sub)}</div>
      </div>
    </div>`;
}

function renderizarKpis(d) {
  const r = d.resumo;
  const cancelamento = r.canceladas
    ? `${plural(r.canceladas, 'cancelada', 'canceladas')} · ${percentual(r.taxa_cancelamento)} do total`
    : 'Nenhuma cancelada';
  const situacoes = [cancelamento];
  if (r.pausadas) situacoes.push(plural(r.pausadas, 'pausada', 'pausadas'));
  if (r.em_teste) situacoes.push(`${plural(r.em_teste, 'em teste', 'em teste')} (sem cobrança ainda)`);

  const cartoes = [
    { icone: 'dinheiro', cor: 'blue', rotulo: 'Gasto mensal', valor: moeda(r.total_mensal), sub: `≈ ${moeda(r.custo_diario)} por dia` },
    { icone: 'calendario', cor: 'blue', rotulo: 'Gasto anual', valor: moeda(r.total_anual), sub: 'Soma anualizada das ativas' },
    { icone: 'ativas', cor: 'green', rotulo: 'Assinaturas ativas', valor: String(r.ativas), sub: situacoes.join(' · ') },
    { icone: 'media', cor: 'amber', rotulo: 'Média por assinatura', valor: `${moeda(r.media_mensal)} / mês`, sub: `Mediana: ${moeda(r.mediana_mensal)} / mês` },
    {
      icone: 'maior', cor: 'red', rotulo: 'Maior assinatura',
      valor: r.maior ? r.maior.nome_servico : '—',
      sub: r.maior ? `${moeda(r.maior.total_mensal)} / mês · ${percentual(r.maior.percentual)} do gasto` : ''
    },
    {
      icone: 'economia', cor: 'green', rotulo: 'Economia com canceladas',
      valor: `${moeda(r.economia_mensal)} / mês`,
      sub: r.canceladas
        ? `${moeda(r.economia_anual)} por ano${r.economia_acumulada ? ` · ${moeda(r.economia_acumulada)} já economizados` : ''}`
        : 'Nada cancelado ainda'
    }
  ];

  document.getElementById('est-kpis').innerHTML = cartoes.map(cartaoKpi).join('');
}

// ── Destaques (insights gerados a partir dos dados) ───────────────
function mesPesadoRelevante(d) {
  const p = d.projecao;
  return p.mes_mais_pesado && p.media_mensal > 0
    && p.mes_mais_pesado.total >= p.media_mensal * LIMIAR_MES_PESADO;
}

// Avisos que não podem ficar de fora do limite de destaques: teste acabando, pausas e câmbio.
function montarAvisos(d) {
  const avisos = [];

  (d.em_teste || []).filter(t => t.dias_restantes <= 7).forEach(t => {
    const quando = t.dias_restantes === 1 ? 'amanhã' : `em ${t.dias_restantes} dias`;
    avisos.push({
      tipo: 'alerta',
      html: `O teste gratuito de ${forte(t.nome_servico)} termina ${quando}. Depois disso serão cobrados ${forte(moeda(t.total_mensal))} por mês (sua parte).`
    });
  });

  if ((d.pausadas || []).length) {
    const mensal = d.pausadas.reduce((soma, p) => soma + p.total_mensal, 0);
    avisos.push({
      tipo: 'ok',
      html: `${plural(d.pausadas.length, 'assinatura pausada', 'assinaturas pausadas')}: enquanto durar a pausa você deixa de gastar ${forte(moeda(mensal))} por mês.`
    });
  }

  if (d.cambio && d.cambio.fonte === 'aproximada') {
    avisos.push({
      tipo: 'alerta',
      html: 'As cotações de câmbio são aproximadas porque a API não respondeu; valores em outras moedas podem variar.'
    });
  }

  return avisos;
}

function montarDestaques(d) {
  const r = d.resumo;
  const itens = [];

  const janela30 = d.proximas_cobrancas.find(j => j.dias === 30);
  if (janela30 && janela30.qtd > 0) {
    itens.push({
      tipo: 'info',
      html: `Nos próximos 30 dias serão cobrados ${forte(moeda(janela30.total))} em ${plural(janela30.qtd, 'renovação', 'renovações')}.`
    });
  }

  if (mesPesadoRelevante(d)) {
    const p = d.projecao;
    const acima = (p.mes_mais_pesado.total / p.media_mensal - 1) * 100;
    itens.push({
      tipo: 'alerta',
      html: `${forte(nomeMes(p.mes_mais_pesado))} será o mês mais pesado: ${forte(moeda(p.mes_mais_pesado.total))}, ${forte(percentual(acima))} acima da média mensal de ${moeda(p.media_mensal)}.`
    });
  }

  if (r.ativas >= 4) {
    itens.push({
      tipo: r.concentracao_top3 >= 70 ? 'alerta' : 'info',
      html: `As 3 maiores assinaturas concentram ${forte(percentual(r.concentracao_top3))} do gasto mensal.`
    });
  }

  if (r.ativas >= 3 && r.maior && r.maior.percentual >= 40) {
    itens.push({
      tipo: 'alerta',
      html: `${forte(r.maior.nome_servico)} sozinha representa ${forte(percentual(r.maior.percentual))} de tudo que você paga.`
    });
  }

  if (d.por_categoria.length >= 2) {
    const c = d.por_categoria[0];
    itens.push({
      tipo: 'info',
      html: `${forte(c.nome_categoria)} é a categoria que mais pesa: ${forte(percentual(c.percentual))} do gasto (${moeda(c.total_mensal)} por mês).`
    });
  }

  const anual = d.por_periodicidade.find(p => p.periodicidade === 'anual');
  if (anual && !mesPesadoRelevante(d)) {
    itens.push({
      tipo: 'info',
      html: `Assinaturas anuais respondem por ${forte(percentual(anual.percentual))} do gasto e são cobradas de uma vez só.`
    });
  }

  const reajustes = d.reajustes;
  if (reajustes.aumentos > 0 && reajustes.recentes.length) {
    const ultimo = reajustes.recentes.find(x => x.valor_novo > x.valor_antigo) || reajustes.recentes[0];
    const variacao = ultimo.variacao_percentual != null ? ` (${formatarVariacao(ultimo.variacao_percentual)})` : '';
    itens.push({
      tipo: 'alerta',
      html: `${plural(reajustes.aumentos, 'aumento de preço registrado', 'aumentos de preço registrados')}. Mais recente: ${forte(ultimo.nome_servico)}${variacao}.`
    });
  }

  if (r.canceladas > 0) {
    itens.push({
      tipo: 'ok',
      html: `Ao cancelar ${plural(r.canceladas, 'serviço', 'serviços')}, você deixou de pagar ${forte(moeda(r.economia_mensal))} por mês (${moeda(r.economia_anual)} por ano)${r.economia_acumulada ? `; desde as datas de cancelamento já são ${forte(moeda(r.economia_acumulada))} economizados` : ''}.`
    });
  }

  return [...montarAvisos(d), ...itens].slice(0, 6);
}

function renderizarDestaques(d) {
  const itens = montarDestaques(d);
  const alvo = document.getElementById('est-insights');
  if (!itens.length) {
    alvo.innerHTML = '<li class="insight"><span class="insight-dot"></span><span>Cadastre mais assinaturas para ver destaques sobre o seu perfil de gastos.</span></li>';
    return;
  }
  alvo.innerHTML = itens
    .map(i => `<li class="insight insight-${i.tipo}"><span class="insight-dot"></span><span>${i.html}</span></li>`)
    .join('');
}

// ── Gráficos ──────────────────────────────────────────────────────
function prepararGraficos() {
  Chart.defaults.color = corCss('--text-muted');
  Chart.defaults.borderColor = corCss('--divider');
  Chart.defaults.font.family = 'Inter';
  Chart.defaults.font.size = 11;
}

function desenhar(id, config) {
  if (graficos[id]) graficos[id].destroy();
  graficos[id] = new Chart(document.getElementById(id), config);
}

function renderizarProjecao(d) {
  prepararGraficos();
  const p = d.projecao;
  const destacarPesado = mesPesadoRelevante(d);
  const azul = corCss('--blue');
  const ambar = corCss('--amber');

  const cores = p.meses.map(m =>
    destacarPesado && m.ano === p.mes_mais_pesado.ano && m.mes === p.mes_mais_pesado.mes ? ambar : azul
  );

  desenhar('chart-projecao', {
    type: 'bar',
    data: {
      labels: p.meses.map(m => `${MESES_CURTOS[m.mes - 1]}/${String(m.ano).slice(2)}`),
      datasets: [
        {
          label: 'Cobrado no mês',
          data: p.meses.map(m => m.total),
          backgroundColor: cores,
          borderRadius: 6,
          maxBarThickness: 34,
          order: 2
        },
        {
          type: 'line',
          label: 'Média mensal',
          data: p.meses.map(() => p.media_mensal),
          borderColor: corCss('--text-muted'),
          borderDash: [6, 4],
          borderWidth: 1.5,
          pointRadius: 0,
          pointHoverRadius: 0,
          order: 1
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { position: 'bottom', labels: { usePointStyle: true, padding: 14 } },
        tooltip: {
          callbacks: {
            label: ctx => ` ${ctx.dataset.label}: ${moeda(ctx.parsed.y)}`,
            afterLabel: ctx => ctx.datasetIndex === 0 ? ` ${plural(p.meses[ctx.dataIndex].qtd, 'cobrança', 'cobranças')}` : ''
          }
        }
      },
      scales: {
        y: { beginAtZero: true, ticks: { callback: v => moedaCurta(v) }, grid: { color: corCss('--divider') } },
        x: { grid: { display: false } }
      }
    }
  });

  const pesado = p.mes_mais_pesado;
  const leve = p.mes_mais_leve;
  document.getElementById('proj-resumo').innerHTML = `
    <div>
      <div class="mini-label">Total em 12 meses</div>
      <div class="mini-valor">${escapar(moeda(p.total_12_meses))}</div>
      <div class="mini-sub">Média de ${escapar(moeda(p.media_mensal))} / mês</div>
    </div>
    <div>
      <div class="mini-label">Mês mais pesado</div>
      <div class="mini-valor">${pesado ? escapar(moeda(pesado.total)) : '—'}</div>
      <div class="mini-sub">${pesado ? escapar(nomeMes(pesado)) : ''}</div>
    </div>
    <div>
      <div class="mini-label">Mês mais leve</div>
      <div class="mini-valor">${leve ? escapar(moeda(leve.total)) : '—'}</div>
      <div class="mini-sub">${leve ? escapar(nomeMes(leve)) : ''}</div>
    </div>`;
}

function renderizarJanelas(d) {
  document.getElementById('janelas-cobranca').innerHTML = d.proximas_cobrancas.map(j => `
    <div class="janela-item">
      <div>
        <div class="janela-nome">Próximos ${j.dias} dias</div>
        <div class="janela-qtd">${escapar(j.qtd ? plural(j.qtd, 'cobrança', 'cobranças') : 'Nenhuma cobrança')}</div>
      </div>
      <div class="janela-valor">${escapar(moeda(j.total))}</div>
    </div>`).join('');
}

function renderizarGraficosPerfil(d) {
  prepararGraficos();
  const fundo = corCss('--white');

  // Periodicidade
  desenhar('chart-periodicidade', {
    type: 'doughnut',
    data: {
      labels: d.por_periodicidade.map(p => PERIODICIDADE_LABEL[p.periodicidade] || p.periodicidade),
      datasets: [{
        data: d.por_periodicidade.map(p => p.total_mensal),
        backgroundColor: d.por_periodicidade.map((_, i) => CORES[i % CORES.length]),
        borderWidth: 2,
        borderColor: fundo,
        hoverOffset: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '62%',
      plugins: {
        legend: { position: 'bottom', labels: { usePointStyle: true, padding: 14 } },
        tooltip: {
          callbacks: {
            label: ctx => {
              const p = d.por_periodicidade[ctx.dataIndex];
              return ` ${ctx.label}: ${moeda(p.total_mensal)} / mês (${percentual(p.percentual)})`;
            },
            afterLabel: ctx => ` ${plural(d.por_periodicidade[ctx.dataIndex].qtd, 'assinatura', 'assinaturas')}`
          }
        }
      }
    }
  });

  // Método de pagamento
  desenhar('chart-pagamento-est', {
    type: 'bar',
    data: {
      labels: d.por_pagamento.map(p => METODOS_PAGAMENTO_LABEL[p.metodo] || p.metodo),
      datasets: [{
        data: d.por_pagamento.map(p => p.total_mensal),
        backgroundColor: corCss('--blue'),
        borderRadius: 6,
        maxBarThickness: 22
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: ctx => {
              const p = d.por_pagamento[ctx.dataIndex];
              return ` ${moeda(p.total_mensal)} / mês (${percentual(p.percentual)})`;
            },
            afterLabel: ctx => ` ${plural(d.por_pagamento[ctx.dataIndex].qtd, 'assinatura', 'assinaturas')}`
          }
        }
      },
      scales: {
        x: { beginAtZero: true, ticks: { callback: v => moedaCurta(v) }, grid: { color: corCss('--divider') } },
        y: { grid: { display: false } }
      }
    }
  });

  // Faixas de valor
  desenhar('chart-faixas', {
    type: 'bar',
    data: {
      labels: d.faixas_valor.map(f => f.rotulo),
      datasets: [{
        data: d.faixas_valor.map(f => f.qtd),
        backgroundColor: corCss('--blue'),
        borderRadius: 6,
        maxBarThickness: 34
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: ctx => ` ${plural(ctx.parsed.y, 'assinatura', 'assinaturas')}` } }
      },
      scales: {
        y: { beginAtZero: true, ticks: { stepSize: 1, precision: 0 }, grid: { color: corCss('--divider') } },
        x: { grid: { display: false }, ticks: { maxRotation: 0, autoSkip: false, font: { size: 10 } } }
      }
    }
  });
}

document.addEventListener('temachange', () => {
  if (!dados || !dados.resumo.ativas || typeof Chart === 'undefined') return;
  renderizarProjecao(dados);
  renderizarGraficosPerfil(dados);
});

// ── Rankings ──────────────────────────────────────────────────────
function itemRanking({ posicao, logo, nome, valor, meta, share, cor }) {
  return `
    <div class="rank-item">
      ${logo || `<div class="rank-pos">${posicao}</div>`}
      <div class="rank-corpo">
        <div class="rank-topo">
          <div class="rank-nome" title="${escapar(nome)}">${escapar(nome)}</div>
          <div class="rank-valor">${escapar(valor)}</div>
        </div>
        <div class="rank-meta">${escapar(meta)}</div>
        <div class="rank-barra"><span style="width:${Math.max(2, Math.min(100, share))}%;background:${cor}"></span></div>
      </div>
    </div>`;
}

function renderizarRankingMaiores(d) {
  document.getElementById('rank-maiores-hint').textContent = `Top ${d.maiores.length} · valor mensal`;
  document.getElementById('rank-maiores').innerHTML = d.maiores.map(a => {
    const per = PERIODICIDADE_LABEL[a.periodicidade] || 'Mensal';
    const original = a.periodicidade === 'mensal' ? '' : ` · ${moeda(a.valor_periodo)} ${a.periodicidade === 'anual' ? 'por ano' : 'por semana'}`;
    return itemRanking({
      logo: logoHtml(a.nome_servico),
      nome: a.nome_servico,
      valor: `${moeda(a.total_mensal)} · ${percentual(a.percentual)}`,
      meta: `${a.categoria} · ${per}${original}`,
      share: a.percentual,
      cor: corCss('--blue')
    });
  }).join('');
}

function renderizarRankingCategorias(d) {
  document.getElementById('rank-categorias').innerHTML = d.por_categoria.map((c, i) => itemRanking({
    posicao: i + 1,
    nome: c.nome_categoria,
    valor: `${moeda(c.total_mensal)} · ${percentual(c.percentual)}`,
    meta: `${plural(c.qtd, 'assinatura', 'assinaturas')} · ticket médio ${moeda(c.ticket_medio)}`,
    share: c.percentual,
    cor: CORES[i % CORES.length]
  })).join('');
}

// ── Atenção: reajustes e canceladas ───────────────────────────────
function formatarVariacao(v) {
  return `${v > 0 ? '+' : ''}${v.toLocaleString('pt-BR', { maximumFractionDigits: 1 })}%`;
}

function formatarData(iso) {
  if (!iso) return '';
  const data = new Date(iso);
  return isNaN(data) ? '' : data.toLocaleDateString('pt-BR');
}

function renderizarReajustes(d) {
  const r = d.reajustes;
  const hint = document.getElementById('reajustes-hint');
  const lista = document.getElementById('lista-reajustes');

  hint.textContent = (r.aumentos || r.reducoes)
    ? `${plural(r.aumentos, 'aumento', 'aumentos')} · ${plural(r.reducoes, 'redução', 'reduções')}`
    : '';

  if (!r.recentes.length) {
    lista.innerHTML = '<div class="empty">Nenhum reajuste registrado. Quando o valor de uma assinatura for alterado, ele aparece aqui.</div>';
    return;
  }

  lista.innerHTML = r.recentes.map(x => {
    const subiu = x.valor_novo > x.valor_antigo;
    const badge = x.variacao_percentual != null
      ? `<span class="variacao ${subiu ? 'variacao-up' : 'variacao-down'}">${escapar(formatarVariacao(x.variacao_percentual))}</span>`
      : '';
    return `
      <div class="linha-item">
        ${logoHtml(x.nome_servico)}
        <div class="linha-info">
          <div class="linha-nome">${escapar(x.nome_servico)}</div>
          <div class="linha-meta">${escapar(moeda(x.valor_antigo))} → ${escapar(moeda(x.valor_novo))} · ${escapar(formatarData(x.data))}</div>
        </div>
        ${badge}
      </div>`;
  }).join('');
}

function renderizarCanceladas(d) {
  const lista = document.getElementById('lista-canceladas');
  const hint = document.getElementById('canceladas-hint');
  const r = d.resumo;

  hint.textContent = r.canceladas ? plural(r.canceladas, 'cancelada', 'canceladas') : '';

  if (!d.canceladas.length) {
    lista.innerHTML = '<div class="empty">Nenhuma assinatura cancelada.</div>';
    return;
  }

  lista.innerHTML = d.canceladas.map(c => `
    <div class="linha-item">
      ${logoHtml(c.nome_servico)}
      <div class="linha-info">
        <div class="linha-nome">${escapar(c.nome_servico)}</div>
        <div class="linha-meta">${escapar(PERIODICIDADE_LABEL[c.periodicidade] || 'Mensal')} · ${escapar(moeda(c.total_anual))} por ano${c.data_cancelamento ? ` · cancelada em ${escapar(dataBr(c.data_cancelamento))}` : ''}${c.economizado ? ` · ${escapar(moeda(c.economizado))} economizados` : ''}</div>
      </div>
      <div class="linha-valor linha-valor-economia">${escapar(moeda(c.total_mensal))} / mês</div>
    </div>`).join('') + `
    <div class="card-rodape">Você deixou de gastar ${forte(moeda(r.economia_mensal))} por mês, ou ${forte(moeda(r.economia_anual))} por ano.${r.economia_acumulada ? ` Desde os cancelamentos, já foram ${forte(moeda(r.economia_acumulada))}.` : ''}</div>`;
}

async function init() {
  const usuario = await protegerPagina();
  if (!usuario) return;
  carregarEstatisticasDetalhadas();
}

init();
