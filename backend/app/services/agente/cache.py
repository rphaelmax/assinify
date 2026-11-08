"""Cache em memória com validade curta.

Protege a cota da API de IA: a análise e a pesquisa de planos só são refeitas
quando os dados do usuário mudam ou quando o tempo expira."""
import threading
import time

_dados = {}
_trava = threading.Lock()
LIMITE_ENTRADAS = 300


def obter(chave):
    with _trava:
        item = _dados.get(chave)
        if item is None:
            return None
        valor, expira = item
        if expira < time.time():
            _dados.pop(chave, None)
            return None
        return valor


def guardar(chave, valor, ttl_segundos=1800):
    with _trava:
        if len(_dados) >= LIMITE_ENTRADAS:
            agora = time.time()
            for k in [k for k, (_, e) in _dados.items() if e < agora] or list(_dados)[:50]:
                _dados.pop(k, None)
        _dados[chave] = (valor, time.time() + ttl_segundos)
