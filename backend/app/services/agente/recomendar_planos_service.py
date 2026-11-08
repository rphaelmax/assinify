import json
from datetime import date

from app import gemini
from app.exceptions import ValidationError
from app.services.agente import cache
from app.services.assinatura.listar_assinaturas_service import ListarAssinaturasService

MAX_SERVICOS = 6   # limita custo e tempo da pesquisa
TTL_SEGUNDOS = 1800

INSTRUCAO = """Você é um consultor brasileiro de economia doméstica especializado em assinaturas digitais. \
Seja objetivo, honesto e nunca invente preços."""

PROMPT = """Hoje é {hoje}. O usuário mora no Brasil. Assinaturas ativas dele (JSON):
{dados}

Para cada serviço, {como_buscar} e diga se existe alternativa mais barata para o perfil dele: pagamento anual, \
plano família/duo/estudante, pacote ou combo, plano com anúncios ou promoção vigente.

Regras:
- Só recomende o que for verificável e informe o preço encontrado e a periodicidade.
- Mostre a economia estimada em R$ por ano, com a conta (preço atual × 12 menos o novo valor).
- Se não houver opção melhor ou não conseguir confirmar o preço, diga isso em vez de inventar.
- Não recomende cancelar.
- Formato: texto simples, uma linha por serviço começando pelo nome, com 1 a 2 frases. Sem tabelas.
- Termine com uma frase curta lembrando de confirmar o preço no site oficial antes de contratar."""

COMO_COM_BUSCA = 'pesquise na web os planos e preços ATUAIS no Brasil (priorize o site oficial)'
COMO_SEM_BUSCA = ('use apenas o que você já sabe sobre os planos no Brasil. Você NÃO tem acesso à web agora: '
                  'deixe claro que os valores podem estar desatualizados e não os apresente como certos')


class RecomendarPlanosService:
    """Caso de uso: sugerir planos mais baratos para as assinaturas ativas do usuário.

    A lista de assinaturas vem do banco (nunca da IA); a IA só pesquisa e compara.
    Usa busca na web quando disponível e, se ela falhar, responde sem busca avisando."""

    @staticmethod
    def executar(usuario_atual, id_assinatura=None):
        from app.services.agente.ferramentas import resumir_assinaturas

        if id_assinatura is not None:
            try:
                id_assinatura = int(id_assinatura)
            except (TypeError, ValueError):
                raise ValidationError('Id da assinatura inválido')

        ativas = ListarAssinaturasService.executar(usuario_atual, {'status': 'ativa'})
        if id_assinatura is not None:
            ativas = [a for a in ativas if a.id_assinatura == id_assinatura]
        if not ativas:
            raise ValidationError('Não há assinaturas ativas para analisar')

        dados = [
            {k: a[k] for k in ('nome_servico', 'plano', 'valor', 'moeda', 'periodicidade', 'num_pessoas', 'categoria')}
            for a in resumir_assinaturas(ativas[:MAX_SERVICOS], usuario_atual)
        ]
        texto_dados = json.dumps(dados, ensure_ascii=False)

        chave = ('planos', usuario_atual.id_usuario, texto_dados)
        em_cache = cache.obter(chave)
        if em_cache:
            return em_cache

        def perguntar(com_busca):
            prompt = PROMPT.format(
                hoje=date.today().strftime('%d/%m/%Y'), dados=texto_dados,
                como_buscar=COMO_COM_BUSCA if com_busca else COMO_SEM_BUSCA,
            )
            return gemini.gerar(
                [{'role': 'user', 'parts': [{'text': prompt}]}], INSTRUCAO,
                busca_web=com_busca, temperatura=0.2,
            )

        try:
            resposta, fundamentado = perguntar(True), True
            if not gemini.texto(resposta):
                raise gemini.IAIndisponivelError('Resposta vazia')
        except gemini.IAIndisponivelError:
            # busca indisponível (cota, plano da chave...): responde sem ela, avisando
            resposta, fundamentado = perguntar(False), False

        texto = gemini.texto(resposta)
        if not texto:
            raise gemini.IAIndisponivelError('A IA não retornou recomendações. Tente novamente')

        resultado = {
            'texto': texto,
            'fontes': gemini.fontes(resposta) if fundamentado else [],
            'fundamentado': fundamentado,
            'servicos_analisados': len(dados),
            'total_ativas': len(ativas),
        }
        cache.guardar(chave, resultado, TTL_SEGUNDOS)
        return resultado
