import json
from datetime import date

from app import gemini
from app.services.agente import cache
from app.services.agente.ferramentas import resumir_assinaturas
from app.services.assinatura.estatisticas_assinatura_service import EstatisticasAssinaturaService
from app.services.assinatura.listar_assinaturas_service import ListarAssinaturasService

TTL_SEGUNDOS = 1800
MAX_INSIGHTS = 3
TIPOS = ('economia', 'alerta', 'info')

SCHEMA = {
    'type': 'OBJECT',
    'properties': {'insights': {'type': 'ARRAY', 'items': {
        'type': 'OBJECT',
        'properties': {
            'titulo': {'type': 'STRING'},
            'texto': {'type': 'STRING'},
            'tipo': {'type': 'STRING', 'enum': list(TIPOS)},
        },
        'required': ['titulo', 'texto', 'tipo'],
    }}},
    'required': ['insights'],
}

INSTRUCAO = """Você é o analista financeiro do Assinify. Escreva em português do Brasil, direto e sem enrolação.

Gere de 2 a 3 insights curtos, usando SOMENTE os dados fornecidos (não invente serviços, preços ou datas). Priorize:
1. alerta: renovações ou fins de teste grátis nos próximos 7 dias (campo dias_ate_renovacao), com nome, valor e data;
2. info: onde está o maior peso do gasto e a projeção para os próximos 12 meses (use total_anual do resumo, que é o gasto anual real do usuário);
3. economia: sobreposição, quando há vários serviços ativos da mesma categoria (ex.: 3 streamings). Sugira revisar quais ainda valem a pena. Você não sabe o quanto o usuário usa cada serviço, então nunca afirme que algo é desperdício.
Se não houver base para um item, pule-o. Cada "texto" tem no máximo 2 frases; "titulo" no máximo 6 palavras. \
Valores em reais como R$ 39,90 (moeda base: {moeda})."""


class GerarInsightsService:
    """Caso de uso: análise proativa do perfil de assinaturas, exibida no dashboard sem o usuário perguntar.

    Os números vêm do backend; a IA só interpreta e prioriza. O resultado fica em cache
    enquanto os dados do usuário não mudam."""

    @staticmethod
    def executar(usuario_atual, forcar=False):
        itens = ListarAssinaturasService.executar(usuario_atual, {})
        if not itens:
            return {'insights': [], 'vazio': True}

        hoje = date.today()
        assinaturas = resumir_assinaturas(itens, usuario_atual)
        for a in assinaturas:
            if a['status'] == 'ativa' and a['proxima_renovacao']:
                a['dias_ate_renovacao'] = (date.fromisoformat(a['proxima_renovacao']) - hoje).days
        resumo = EstatisticasAssinaturaService.executar(usuario_atual)
        resumo.pop('cambio', None)

        dados = json.dumps({'hoje': hoje.isoformat(), 'resumo': resumo, 'assinaturas': assinaturas},
                           ensure_ascii=False, sort_keys=True, default=str)
        chave = ('insights', usuario_atual.id_usuario, dados)
        if not forcar:
            em_cache = cache.obter(chave)
            if em_cache:
                return em_cache

        try:
            resposta = gemini.gerar(
                [{'role': 'user', 'parts': [{'text': 'Dados do usuário (JSON):\n' + dados}]}],
                INSTRUCAO.format(moeda=usuario_atual.moeda_base or 'BRL'),
                schema_json=SCHEMA, temperatura=0.3,
            )
            insights = GerarInsightsService._ler(gemini.texto(resposta))
        except gemini.IAIndisponivelError as erro:
            # o dashboard não pode quebrar por causa da IA: devolve vazio com o motivo
            return {'insights': [], 'indisponivel': True, 'motivo': erro.mensagem}

        if not insights:
            return {'insights': [], 'indisponivel': True, 'motivo': 'A IA não retornou uma análise válida'}

        resultado = {'insights': insights}
        cache.guardar(chave, resultado, TTL_SEGUNDOS)
        return resultado

    @staticmethod
    def _ler(bruto):
        try:
            itens = json.loads(bruto).get('insights', [])
        except (ValueError, AttributeError):
            return []
        limpos = []
        for item in itens if isinstance(itens, list) else []:
            if not isinstance(item, dict) or not item.get('titulo') or not item.get('texto'):
                continue
            tipo = item.get('tipo') if item.get('tipo') in TIPOS else 'info'
            limpos.append({'titulo': str(item['titulo'])[:80], 'texto': str(item['texto'])[:320], 'tipo': tipo})
        return limpos[:MAX_INSIGHTS]
