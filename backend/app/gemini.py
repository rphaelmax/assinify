"""Cliente mínimo da API Gemini (generateContent), sem dependências extras.

Mesmo estilo de app/cambio.py: só urllib, timeout curto e erro tratado.
Se o modelo principal estiver fora do ar, sem cota ou inexistente, tenta
o modelo reserva (GEMINI_MODEL_FALLBACK) antes de desistir.
"""
import json
import logging
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from flask import current_app

from app.exceptions import AppError

logger = logging.getLogger(__name__)

URL_BASE = 'https://generativelanguage.googleapis.com/v1beta/models'
TIMEOUT_SEGUNDOS = 30
# Erros em que vale tentar de novo / trocar de modelo (cota, instabilidade, modelo inexistente)
STATUS_TRANSITORIOS = {404, 429, 500, 502, 503, 504}


class IAIndisponivelError(AppError):
    status_code = 503


def _chamar(modelo, chave, corpo):
    pedido = Request(
        f'{URL_BASE}/{modelo}:generateContent',
        data=json.dumps(corpo).encode('utf-8'),
        headers={'Content-Type': 'application/json', 'x-goog-api-key': chave},
        method='POST',
    )
    with urlopen(pedido, timeout=TIMEOUT_SEGUNDOS) as resposta:
        return json.loads(resposta.read().decode('utf-8'))


def gerar(contents, instrucao_sistema, declaracoes_ferramentas=None, busca_web=False,
          schema_json=None, temperatura=0.3):
    """Uma chamada ao modelo. Três modos, que não se misturam:
    - declaracoes_ferramentas: o modelo pode chamar funções (agente do chat);
    - busca_web=True: o modelo pesquisa no Google antes de responder (recomendação de planos);
    - schema_json: a resposta vem como JSON no formato dado (insights do dashboard)."""
    chave = current_app.config.get('GEMINI_API_KEY')
    if not chave:
        raise IAIndisponivelError('O agente de IA não está configurado (falta GEMINI_API_KEY no servidor)')

    config = {'temperature': temperatura}
    if schema_json:
        config['responseMimeType'] = 'application/json'
        config['responseSchema'] = schema_json

    corpo = {
        'systemInstruction': {'parts': [{'text': instrucao_sistema}]},
        'contents': contents,
        'generationConfig': config,
    }
    if busca_web:
        corpo['tools'] = [{'google_search': {}}]
    elif declaracoes_ferramentas:
        corpo['tools'] = [{'functionDeclarations': declaracoes_ferramentas}]

    modelos = [m for m in (
        current_app.config.get('GEMINI_MODEL'),
        current_app.config.get('GEMINI_MODEL_FALLBACK'),
    ) if m]

    for modelo in modelos:
        for tentativa in range(2):
            try:
                return _chamar(modelo, chave, corpo)
            except HTTPError as erro:
                detalhe = erro.read().decode('utf-8', 'replace')[:300]
                logger.warning('Gemini %s respondeu %s: %s', modelo, erro.code, detalhe)
                if erro.code in (400, 401, 403):
                    raise IAIndisponivelError('A chave da Gemini foi recusada. Verifique GEMINI_API_KEY')
                if erro.code not in STATUS_TRANSITORIOS:
                    raise IAIndisponivelError('A IA recusou a requisição')
                if erro.code in (404, 429):
                    break  # tentar de novo no mesmo modelo não adianta; passa para o reserva
                time.sleep(1)
            except (URLError, TimeoutError, OSError) as erro:
                logger.warning('Gemini %s inacessível: %s', modelo, erro)
                time.sleep(1)

    raise IAIndisponivelError('A IA está indisponível no momento. Tente novamente em instantes')


def texto(resposta):
    """Concatena o texto da primeira candidata (ignora partes de raciocínio e chamadas de função)."""
    candidatos = resposta.get('candidates') or []
    if not candidatos:
        return ''
    partes = (candidatos[0].get('content') or {}).get('parts') or []
    return ''.join(p.get('text', '') for p in partes if p.get('text') and not p.get('thought')).strip()


def fontes(resposta, maximo=5):
    """Links usados pela busca na web (groundingMetadata), sem repetidos."""
    candidatos = resposta.get('candidates') or []
    if not candidatos:
        return []
    chunks = (candidatos[0].get('groundingMetadata') or {}).get('groundingChunks') or []
    vistos, lista = set(), []
    for chunk in chunks:
        web = chunk.get('web') or {}
        url = web.get('uri')
        if not url or not url.startswith('https://') or url in vistos:
            continue
        vistos.add(url)
        lista.append({'titulo': (web.get('title') or url)[:80], 'url': url})
        if len(lista) >= maximo:
            break
    return lista
