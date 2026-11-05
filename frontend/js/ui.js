const UI = (() => {
    const ICONES = {
        sucesso: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>',
        erro: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>',
        info: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>',
        alerta: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>'
    };

    function el(tag, classe, texto) {
        const n = document.createElement(tag);
        if (classe) n.className = classe;
        if (texto !== undefined) n.textContent = texto;
        return n;
    }

    function areaToasts() {
        let area = document.getElementById('toast-area');
        if (!area) {
            area = el('div', 'toast-area');
            area.id = 'toast-area';
            area.setAttribute('aria-live', 'polite');
            document.body.appendChild(area);
        }
        return area;
    }

    function toast(mensagem, tipo = 'info', duracao = 4000) {
        const t = el('div', `toast toast-${tipo}`);
        t.setAttribute('role', tipo === 'erro' ? 'alert' : 'status');
        const icone = el('span', 'toast-icone');
        icone.innerHTML = ICONES[tipo] || ICONES.info;
        const texto = el('span', 'toast-texto', mensagem);
        const fechar = el('button', 'toast-fechar', '×');
        fechar.type = 'button';
        fechar.setAttribute('aria-label', 'Fechar');
        t.append(icone, texto, fechar);

        const remover = () => {
            if (!t.parentNode) return;
            t.classList.add('saindo');
            setTimeout(() => t.remove(), 200);
        };
        fechar.addEventListener('click', remover);
        areaToasts().appendChild(t);
        setTimeout(remover, duracao);
    }

    function abrir({ titulo, mensagem, corpoHtml, perigo = false, textoConfirmar = 'Confirmar', textoCancelar = 'Cancelar' }) {
        return new Promise((resolve) => {
            const anterior = document.activeElement;
            const overlay = el('div', 'modal-overlay ui-dialog');
            const caixa = el('div', 'modal ui-dialog-box');
            caixa.setAttribute('role', 'dialog');
            caixa.setAttribute('aria-modal', 'true');
            caixa.setAttribute('aria-labelledby', 'ui-dialog-titulo');

            if (perigo) {
                const icone = el('div', 'ui-dialog-icone');
                icone.innerHTML = ICONES.alerta;
                caixa.appendChild(icone);
            }

            const tituloEl = el('div', 'modal-title', titulo);
            tituloEl.id = 'ui-dialog-titulo';
            caixa.appendChild(tituloEl);

            if (mensagem) caixa.appendChild(el('p', 'ui-dialog-texto', mensagem));
            if (corpoHtml) {
                const corpo = el('div', 'ui-dialog-corpo');
                corpo.innerHTML = corpoHtml;
                caixa.appendChild(corpo);
            }

            const acoes = el('div', 'modal-actions');
            let btnCancelar = null;
            if (textoCancelar) {
                btnCancelar = el('button', 'btn-cancel', textoCancelar);
                btnCancelar.type = 'button';
                acoes.appendChild(btnCancelar);
            }
            const btnConfirmar = el('button', perigo ? 'btn-save btn-danger' : 'btn-save', textoConfirmar);
            btnConfirmar.type = 'button';
            acoes.appendChild(btnConfirmar);
            caixa.appendChild(acoes);
            overlay.appendChild(caixa);
            document.body.appendChild(overlay);

            const teclas = (e) => {
                if (e.key === 'Escape') {
                    e.preventDefault();
                    fechar(false);
                    return;
                }
                if (e.key !== 'Tab') return;
                const botoes = [...caixa.querySelectorAll('button')];
                const primeiro = botoes[0];
                const ultimo = botoes[botoes.length - 1];
                if (e.shiftKey && document.activeElement === primeiro) {
                    e.preventDefault();
                    ultimo.focus();
                } else if (!e.shiftKey && document.activeElement === ultimo) {
                    e.preventDefault();
                    primeiro.focus();
                }
            };

            function fechar(resultado) {
                document.removeEventListener('keydown', teclas);
                overlay.remove();
                if (anterior && anterior.focus) anterior.focus();
                resolve(resultado);
            }

            document.addEventListener('keydown', teclas);
            overlay.addEventListener('click', (e) => { if (e.target === overlay) fechar(false); });
            btnConfirmar.addEventListener('click', () => fechar(true));
            if (btnCancelar) btnCancelar.addEventListener('click', () => fechar(false));

            overlay.classList.add('open');
            (btnCancelar || btnConfirmar).focus();
        });
    }

    function confirmar(opcoes) {
        return abrir(opcoes);
    }

    function informar({ titulo, corpoHtml, textoFechar = 'Fechar' }) {
        return abrir({ titulo, corpoHtml, textoConfirmar: textoFechar, textoCancelar: null });
    }

    function erroForm(id, mensagem) {
        const alvo = document.getElementById(id);
        if (!alvo) return;
        alvo.textContent = mensagem;
        alvo.className = 'form-feedback form-feedback-erro';
    }

    function limparErroForm(id) {
        const alvo = document.getElementById(id);
        if (!alvo) return;
        alvo.textContent = '';
        alvo.className = 'form-feedback';
    }

    document.addEventListener('keydown', (e) => {
        if (e.key !== 'Escape') return;
        if (document.querySelector('.modal-overlay.ui-dialog.open')) return;
        const abertos = document.querySelectorAll('.modal-overlay.open');
        if (abertos.length) abertos[abertos.length - 1].classList.remove('open');
    });

    return { toast, confirmar, informar, erroForm, limparErroForm };
})();