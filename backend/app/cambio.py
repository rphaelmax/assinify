"""Conversão entre moedas.

As cotações vêm da API pública open.er-api.com (sem chave, atualiza 1x por
dia, exige atribuição: "Rates By Exchange Rate API"). Ordem de preferência:

1. cache em memória;
2. cotação salva no banco, se tiver menos de 12 h;
3. API (e grava o resultado no banco);
4. última cotação salva no banco, mesmo antiga;
5. COTACOES_APROXIMADAS, só para o app nunca quebrar sem internet.

Todas as cotações são "unidades da moeda por 1 USD"; a conversão entre duas
moedas quaisquer passa por esse pivô.
"""
import json
import logging
import threading
from datetime import datetime, timedelta
from decimal import Decimal
from urllib.request import Request, urlopen

from app.moedas import MOEDAS, MOEDA_PADRAO

logger = logging.getLogger(__name__)

URL_COTACOES = 'https://open.er-api.com/v6/latest/USD'
VALIDADE_COTACAO = timedelta(hours=12)
ESPERA_APOS_FALHA = timedelta(minutes=10)
TIMEOUT_SEGUNDOS = 4

# Valores aproximados, usados SOMENTE se a API estiver inacessível e não houver
# nenhuma cotação salva (ex.: primeiro start sem internet). O front avisa
# quando é este o caso (fonte == 'aproximada').
COTACOES_APROXIMADAS = {
    'USD': Decimal('1'), 'BRL': Decimal('5.40'), 'EUR': Decimal('0.92'),
    'GBP': Decimal('0.79'), 'CAD': Decimal('1.37'), 'AUD': Decimal('1.50'),
    'JPY': Decimal('150'), 'CHF': Decimal('0.88'), 'ARS': Decimal('1000'),
    'MXN': Decimal('18.5'),
}

_lock = threading.Lock()
_estado = {'taxas': None, 'fonte': None, 'atualizada_em': None, 'valido_ate': None}


def _agora():
    return datetime.utcnow()


def _buscar_na_api():
    pedido = Request(URL_COTACOES, headers={'User-Agent': 'Assinify/1.0'})
    with urlopen(pedido, timeout=TIMEOUT_SEGUNDOS) as resposta:
        corpo = json.loads(resposta.read().decode('utf-8'))
    if corpo.get('result') != 'success':
        raise ValueError('Resposta da API de câmbio sem sucesso')
    taxas = {}
    for moeda in MOEDAS:
        valor = (corpo.get('rates') or {}).get(moeda)
        if valor is None or valor <= 0:
            raise ValueError(f'Cotação ausente para {moeda}')
        taxas[moeda] = Decimal(str(valor))
    return taxas


def _ler_do_banco():
    from app.models.taxa_cambio import TaxaCambio
    linhas = TaxaCambio.query.all()
    taxas = {l.moeda: Decimal(str(l.taxa_por_usd)) for l in linhas if l.moeda in MOEDAS}
    if set(taxas) != set(MOEDAS):
        return None, None  # vazio ou incompleto (ex.: moeda nova no código)
    return taxas, min(l.atualizada_em for l in linhas)


def _gravar_no_banco(taxas):
    from app.extensions import db
    from app.models.taxa_cambio import TaxaCambio
    agora = _agora()
    for moeda, taxa in taxas.items():
        db.session.merge(TaxaCambio(moeda=moeda, taxa_por_usd=taxa, atualizada_em=agora))
    db.session.commit()


def _tentar_banco(funcao, *args):
    """Falha de banco nunca deve derrubar uma consulta de valores."""
    try:
        return funcao(*args)
    except Exception:
        logger.exception('Falha ao acessar a tabela taxas_cambio')
        try:
            from app.extensions import db
            db.session.rollback()
        except Exception:
            pass
        return None


def _carregar():
    agora = _agora()
    salvas, salvas_em = _tentar_banco(_ler_do_banco) or (None, None)

    if salvas and agora - salvas_em < VALIDADE_COTACAO:
        return {'taxas': salvas, 'fonte': 'banco', 'atualizada_em': salvas_em,
                'valido_ate': salvas_em + VALIDADE_COTACAO}

    try:
        taxas = _buscar_na_api()
    except Exception:
        logger.warning('API de câmbio indisponível; usando a última cotação conhecida', exc_info=True)
        valido_ate = agora + ESPERA_APOS_FALHA
        if salvas:
            return {'taxas': salvas, 'fonte': 'salva', 'atualizada_em': salvas_em, 'valido_ate': valido_ate}
        return {'taxas': dict(COTACOES_APROXIMADAS), 'fonte': 'aproximada',
                'atualizada_em': None, 'valido_ate': valido_ate}

    _tentar_banco(_gravar_no_banco, taxas)
    return {'taxas': taxas, 'fonte': 'api', 'atualizada_em': agora, 'valido_ate': agora + VALIDADE_COTACAO}


def _taxas():
    with _lock:
        if _estado['taxas'] is None or _agora() >= _estado['valido_ate']:
            _estado.update(_carregar())
        return _estado['taxas']


def fator(de, para):
    """Quanto vale 1 unidade de `de` em `para` (Decimal)."""
    de = (de or MOEDA_PADRAO).upper()
    para = (para or MOEDA_PADRAO).upper()
    if de == para:
        return Decimal('1')
    taxas = _taxas()
    if de not in taxas or para not in taxas:
        logger.warning('Moeda sem cotação: %s -> %s', de, para)
        return Decimal('1')
    return taxas[para] / taxas[de]


def converter(valor, de, para):
    return Decimal(str(valor)) * fator(de, para)


def info():
    """Origem e data da cotação em uso (sem disparar nenhuma busca)."""
    atualizada = _estado['atualizada_em']
    return {
        'fonte': _estado['fonte'],
        'atualizada_em': atualizada.isoformat() if atualizada else None,
    }


def _reiniciar():
    """Limpa o cache em memória (usado em testes)."""
    with _lock:
        _estado.update({'taxas': None, 'fonte': None, 'atualizada_em': None, 'valido_ate': None})
