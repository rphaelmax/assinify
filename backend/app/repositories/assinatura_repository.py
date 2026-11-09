from collections import namedtuple
from decimal import Decimal

from app.models.assinatura import Assinatura
from app.models.categoria import Categoria

# Colunas permitidas para ordenação — evita SQL injection via query param
ORDENACAO_PERMITIDA = {
    'nome_servico': Assinatura.nome_servico,
    'valor_mensal': Assinatura.valor_mensal,
    'data_renovacao': Assinatura.data_renovacao,
    'status': Assinatura.status,
}

LinhaCategoria = namedtuple('LinhaCategoria', 'id_categoria nome_categoria total qtd')
LinhaPagamento = namedtuple('LinhaPagamento', 'metodo_pagamento total qtd')


def _cobrando(ativas):
    """Ativas que já estão sendo cobradas (fora do teste gratuito)."""
    return [a for a in ativas if not a.em_teste()]


class AssinaturaRepository:
    """Consultas de Assinatura que vão além do CRUD básico (que fica na Model).

    Recebe critérios já validados pelo Service e devolve dados prontos para
    o caso de uso; não conhece HTTP nem regras de negócio.
    """

    # ---------- listagem com filtros ----------

    @staticmethod
    def _filtrar(id_usuario, filtros):
        query = Assinatura.query.filter_by(id_usuario=id_usuario)

        if filtros.get('busca'):
            query = query.filter(Assinatura.nome_servico.ilike(f"%{filtros['busca']}%"))
        if filtros.get('id_categoria') is not None:
            query = query.filter(Assinatura.id_categoria == filtros['id_categoria'])
        if filtros.get('status'):
            query = query.filter(Assinatura.status == filtros['status'])
        if filtros.get('metodo_pagamento'):
            query = query.filter(Assinatura.metodo_pagamento == filtros['metodo_pagamento'])
        if filtros.get('periodicidade'):
            query = query.filter(Assinatura.periodicidade == filtros['periodicidade'])

        return query

    @staticmethod
    def contar_filtradas(id_usuario, filtros):
        return AssinaturaRepository._filtrar(id_usuario, filtros).count()

    @staticmethod
    def listar_filtradas(id_usuario, filtros, ordenar_por=None, ordem=None, offset=None, limit=None):
        query = AssinaturaRepository._filtrar(id_usuario, filtros)

        coluna = ORDENACAO_PERMITIDA.get(ordenar_por or 'data_renovacao', Assinatura.data_renovacao)
        query = query.order_by(coluna.desc() if ordem == 'desc' else coluna.asc())

        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)
        return query.all()

    @staticmethod
    def listar_ativas(id_usuario):
        return Assinatura.query.filter_by(id_usuario=id_usuario, status='ativa').all()

    # ---------- agregações do dashboard ----------
    #
    # Feitas em Python (e não em SQL) porque cada valor precisa ser dividido
    # entre as pessoas, convertido de moeda e ignorar assinaturas em teste
    # gratuito; o volume por usuário é pequeno. Tudo sai na moeda base.

    @staticmethod
    def totais(id_usuario, moeda_base):
        """Total anualizado (parte do usuário, só quem já cobra) e contagens por situação."""
        ativas = AssinaturaRepository.listar_ativas(id_usuario)
        cobrando = _cobrando(ativas)
        total_anual = sum((a.anualizado_em(moeda_base) for a in cobrando), Decimal('0'))

        base = Assinatura.query.filter_by(id_usuario=id_usuario)
        return {
            'total_anual': total_anual,
            'ativas': len(ativas),
            'cobrando': len(cobrando),
            'em_teste': len(ativas) - len(cobrando),
            'pausadas': base.filter_by(status='pausada').count(),
            'canceladas': base.filter_by(status='cancelada').count(),
        }

    @staticmethod
    def gasto_por_categoria(id_usuario, moeda_base):
        nomes = {c.id_categoria: c.nome_categoria for c in Categoria.listar_por_usuario(id_usuario)}
        grupos = {}
        for a in _cobrando(AssinaturaRepository.listar_ativas(id_usuario)):
            grupo = grupos.setdefault(a.id_categoria, [Decimal('0'), 0])
            grupo[0] += a.anualizado_em(moeda_base)
            grupo[1] += 1
        linhas = [
            LinhaCategoria(id_cat, nomes.get(id_cat, 'Sem categoria'), total, qtd)
            for id_cat, (total, qtd) in grupos.items()
        ]
        return sorted(linhas, key=lambda l: l.total, reverse=True)

    @staticmethod
    def gasto_por_pagamento(id_usuario, moeda_base):
        grupos = {}
        for a in _cobrando(AssinaturaRepository.listar_ativas(id_usuario)):
            grupo = grupos.setdefault(a.metodo_pagamento, [Decimal('0'), 0])
            grupo[0] += a.anualizado_em(moeda_base)
            grupo[1] += 1
        return [LinhaPagamento(metodo, total, qtd) for metodo, (total, qtd) in grupos.items()]
