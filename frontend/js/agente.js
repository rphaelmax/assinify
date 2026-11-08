// Assistente de IA do Assinify: botão flutuante + chat que age sobre as assinaturas do usuário.
// Depende de api.js (apiFetch, escapar). Após qualquer alteração, recarrega o dashboard.
(function () {
  const SUGESTOES = [
    'Quanto gasto por mês?',
    'Quais renovam essa semana?',
    'Adicione Netflix R$ 39,90 todo dia 20',
  ];
  const historico = []; // {role: 'user'|'model', text}
  let ocupado = false;

  const ICONE = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l1.9 4.6L18.5 9.5l-4.6 1.9L12 16l-1.9-4.6L5.5 9.5l4.6-1.9L12 3z"/><path d="M19 15l.8 2 2 .8-2 .8-.8 2-.8-2-2-.8 2-.8.8-2z"/></svg>';

  function el(tag, classe, html) {
    const e = document.createElement(tag);
    if (classe) e.className = classe;
    if (html !== undefined) e.innerHTML = html;
    return e;
  }

  // Escapa o texto e só então aplica **negrito**, para nunca injetar HTML vindo da IA.
  function formatar(texto) {
    return escapar(texto).replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  }

  const fab = el('button', 'agente-fab', ICONE);
  fab.setAttribute('aria-label', 'Abrir assistente de IA');
  const painel = el('div', 'agente-panel');
  painel.innerHTML = `
    <div class="agente-head">
      <div class="agente-head-icon">${ICONE}</div>
      <div class="agente-head-txt">
        <div class="agente-head-title">Assistente Assinify</div>
        <div class="agente-head-sub">Cria, altera e consulta suas assinaturas</div>
      </div>
      <button class="agente-close" aria-label="Fechar">&times;</button>
    </div>
    <div class="agente-msgs" id="agente-msgs"></div>
    <div class="agente-sugestoes" id="agente-sugestoes"></div>
    <form class="agente-form" id="agente-form">
      <textarea class="agente-input" id="agente-input" rows="1" maxlength="600"
        placeholder=""></textarea>
      <button class="agente-send" id="agente-send" type="submit">Enviar</button>
    </form>`;

  const msgs = painel.querySelector('#agente-msgs');
  const sugestoes = painel.querySelector('#agente-sugestoes');
  const form = painel.querySelector('#agente-form');
  const input = painel.querySelector('#agente-input');
  const enviar = painel.querySelector('#agente-send');

  function rolar() { msgs.scrollTop = msgs.scrollHeight; }

  function adicionar(classe, texto) {
    const m = el('div', 'agente-msg ' + classe);
    if (classe === 'bot') m.innerHTML = formatar(texto); else m.textContent = texto;
    msgs.appendChild(m);
    rolar();
    return m;
  }

  function atualizarTela() {
    const funcoes = ['carregarCategorias', 'carregarAssinaturas', 'carregarEstatisticas', 'carregarAgenda'];
    funcoes.forEach((nome) => {
      try { if (typeof window[nome] === 'function') window[nome](); } catch { }
    });
    carregarInsights(false);
  }

  // Links das fontes da busca na web (só https; texto sempre escapado).
  function blocoFontes(fontes) {
    const box = el('div', 'agente-fontes');
    const links = fontes
      .filter((f) => typeof f.url === 'string' && f.url.startsWith('https://'))
      .map((f) => `<a href="${escapar(f.url)}" target="_blank" rel="noopener noreferrer">${escapar(f.titulo || f.url)}</a>`);
    box.innerHTML = 'Fontes: ' + links.join(' · ');
    return box;
  }

  // ── Análise proativa (cartão no dashboard) ─────────────────────
  const ROTULO_TIPO = { alerta: 'Atenção', economia: 'Economia', info: 'Resumo' };
  let alvoInsights = null;
  let carregandoInsights = false;

  async function carregarInsights(forcar) {
    alvoInsights = alvoInsights || document.getElementById('agente-insights');
    if (!alvoInsights || carregandoInsights) return;
    carregandoInsights = true;
    if (!alvoInsights.firstChild) {
      alvoInsights.innerHTML = '<div class="card ag-ins"><div class="ag-ins-vazio">✨ Analisando suas assinaturas…</div></div>';
    }
    try {
      const res = await apiFetch('/agente/insights' + (forcar ? '?atualizar=1' : ''));
      const d = await res.json().catch(() => ({}));
      if (!res.ok || d.vazio) { alvoInsights.innerHTML = ''; return; }
      renderizarInsights(d);
    } catch (e) {
      alvoInsights.innerHTML = '';
    } finally {
      carregandoInsights = false;
    }
  }

  function renderizarInsights(d) {
    const itens = (d.insights || []).map((i) => `
      <div class="ag-ins-item ${escapar(i.tipo)}">
        <span class="ag-ins-tag">${escapar(ROTULO_TIPO[i.tipo] || 'Resumo')}</span>
        <div><div class="ag-ins-titulo">${escapar(i.titulo)}</div><div class="ag-ins-texto">${escapar(i.texto)}</div></div>
      </div>`).join('');
    alvoInsights.innerHTML = `
      <div class="card ag-ins">
        <div class="ag-ins-head">
          <div class="ag-ins-title"><span class="ag-ins-ico">${ICONE}</span>Análise do assistente</div>
          <button class="agente-btn" id="ag-ins-atualizar" title="Refazer análise">↻ Atualizar</button>
        </div>
        ${itens || `<div class="ag-ins-vazio">${escapar(d.indisponivel ? 'A análise está indisponível no momento.' : 'Sem insights por enquanto.')}</div>`}
        <div class="ag-ins-planos">
          <button class="agente-btn" id="ag-ins-planos">Buscar planos mais baratos</button>
          <span class="ag-ins-hint">Pesquisa preços atuais na web (~15 s)</span>
        </div>
        <div id="ag-ins-resultado"></div>
      </div>`;
    alvoInsights.querySelector('#ag-ins-atualizar').onclick = () => carregarInsights(true);
    alvoInsights.querySelector('#ag-ins-planos').onclick = buscarPlanos;
  }

  async function buscarPlanos() {
    const btn = document.getElementById('ag-ins-planos');
    const saida = document.getElementById('ag-ins-resultado');
    if (!btn || !saida) return;
    btn.disabled = true;
    saida.innerHTML = '<div class="ag-ins-vazio">Pesquisando planos e preços atuais…</div>';
    try {
      const res = await apiFetch('/agente/planos', { method: 'POST', body: JSON.stringify({}) });
      const d = await res.json().catch(() => ({}));
      if (!res.ok) { saida.innerHTML = `<div class="agente-msg erro">${escapar(d.erro || 'Não foi possível pesquisar agora.')}</div>`; return; }
      const aviso = d.fundamentado
        ? 'Preços encontrados na web agora. Confirme no site oficial antes de contratar.'
        : 'Sem acesso à busca na web: valores podem estar desatualizados. Confirme no site oficial.';
      saida.innerHTML = `<div class="ag-planos-texto">${formatar(d.texto)}</div>
        <div class="ag-planos-aviso ${d.fundamentado ? '' : 'alerta'}">${escapar(aviso)}</div>`;
      if ((d.fontes || []).length) saida.appendChild(blocoFontes(d.fontes));
    } catch (e) {
      if (e.message !== 'Sessão expirada') saida.innerHTML = '<div class="agente-msg erro">Sem conexão com o servidor.</div>';
    } finally {
      btn.disabled = false;
    }
  }

  function cartaoConfirmacao(c) {
    const box = el('div', 'agente-confirma');
    box.innerHTML = `Excluir definitivamente <strong>${escapar(c.nome_servico)}</strong>?
      <div class="agente-confirma-btns">
        <button class="agente-btn perigo" data-ok>Confirmar exclusão</button>
        <button class="agente-btn" data-nao>Cancelar</button>
      </div>`;
    const ok = box.querySelector('[data-ok]');
    const nao = box.querySelector('[data-nao]');
    nao.onclick = () => box.remove();
    ok.onclick = async () => {
      ok.disabled = nao.disabled = true;
      try {
        const res = await apiFetch(`/assinaturas/${c.id_assinatura}`, { method: 'DELETE' });
        if (res.status === 204) {
          box.replaceWith(el('div', 'agente-acao', `✓ "${escapar(c.nome_servico)}" excluída`));
          atualizarTela();
        } else {
          const j = await res.json().catch(() => ({}));
          box.replaceWith(el('div', 'agente-msg erro', escapar(j.erro || 'Não foi possível excluir.')));
        }
      } catch { box.replaceWith(el('div', 'agente-msg erro', 'Falha de conexão ao excluir.')); }
    };
    msgs.appendChild(box);
    rolar();
  }

  async function mandar(texto) {
    texto = (texto || '').trim();
    if (!texto || ocupado) return;
    ocupado = true; enviar.disabled = true;
    sugestoes.style.display = 'none';
    adicionar('user', texto);
    input.value = '';
    const pensando = adicionar('bot pensando', 'Pensando…');

    try {
      const res = await apiFetch('/agente', {
        method: 'POST',
        body: JSON.stringify({ mensagem: texto, historico: historico.slice(-10) }),
      });
      const dados = await res.json().catch(() => ({}));
      pensando.remove();
      if (!res.ok) {
        adicionar('erro', dados.erro || 'O assistente não respondeu. Tente de novo.');
      } else {
        historico.push({ role: 'user', text: texto }, { role: 'model', text: dados.resposta });
        (dados.acoes || []).forEach((a) => msgs.appendChild(el('div', 'agente-acao', '✓ ' + escapar(a.descricao))));
        adicionar('bot', dados.resposta);
        if ((dados.fontes || []).length) msgs.appendChild(blocoFontes(dados.fontes));
        (dados.confirmacoes || []).forEach(cartaoConfirmacao);
        if (dados.houve_alteracao) atualizarTela();
      }
    } catch (e) {
      pensando.remove();
      if (e.message !== 'Sessão expirada') adicionar('erro', 'Sem conexão com o servidor.');
    } finally {
      ocupado = false; enviar.disabled = false; input.focus(); rolar();
    }
  }

  function abrir() {
    painel.classList.toggle('open');
    if (painel.classList.contains('open')) {
      if (!msgs.children.length) adicionar('bot', 'Olá! Posso adicionar, alterar, pausar ou consultar suas assinaturas. É só pedir.');
      input.focus();
    }
  }

  SUGESTOES.forEach((s) => {
    const chip = el('button', 'agente-chip');
    chip.type = 'button'; chip.textContent = s;
    chip.onclick = () => mandar(s);
    sugestoes.appendChild(chip);
  });

  fab.onclick = abrir;
  painel.querySelector('.agente-close').onclick = () => painel.classList.remove('open');
  form.onsubmit = (e) => { e.preventDefault(); mandar(input.value); };
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); mandar(input.value); }
  });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') painel.classList.remove('open'); });

  document.body.appendChild(painel);
  document.body.appendChild(fab);
  carregarInsights(false);
})();
