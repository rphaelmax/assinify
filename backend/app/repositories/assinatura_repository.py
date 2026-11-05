from sqlalchemy import case, func

from app.extensions import db
from app.models.assinatura import Assinatura
from app.models.categoria import Categoria

# Colunas permitidas para ordenação — evita SQL injection via query param
ORDENACAO_PERMITIDA = {
    'nome_servico': Assinatura.nome_servico,
    'valor_mensal': Assinatura.valor_mensal,
    'data_renovacao': Assinatura.data_renovacao,
    'status': Assinatura.status,
}

def _anualizado():
    """Expressão SQL que converte valor_mensal (valor por período) em valor anual."""
    return case(
        (Assinatura.periodicidade == 'semanal', Assinatura.valor_mensal * 52),
        (Assinatura.periodicidade == 'anual', Assinatura.valor_mensal * 1),
        else_=Assinatura.valor_mensal * 12
    )

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

    @staticmethod
    def totais(id_usuario):
        """Total anualizado das ativas e contagem por status."""
        total_anual = db.session.query(
            func.coalesce(func.sum(_anualizado()), 0)
        ).filter(
            Assinatura.id_usuario == id_usuario,
            Assinatura.status == 'ativa'
        ).scalar()

        base = Assinatura.query.filter_by(id_usuario=id_usuario)
        return {
            'total_anual': total_anual,
            'ativas': base.filter_by(status='ativa').count(),
            'canceladas': base.filter_by(status='cancelada').count(),
        }

    @staticmethod
    def gasto_por_categoria(id_usuario):
        anualizado = _anualizado()
        return (
            db.session.query(
                Categoria.id_categoria,
                Categoria.nome_categoria,
                func.coalesce(func.sum(anualizado), 0).label('total'),
                func.count(Assinatura.id_assinatura).label('qtd'),
            )
            .join(Assinatura, Assinatura.id_categoria == Categoria.id_categoria)
            .filter(
                Assinatura.id_usuario == id_usuario,
                Assinatura.status == 'ativa',
            )
            .group_by(Categoria.id_categoria, Categoria.nome_categoria)
            .order_by(func.sum(anualizado).desc())
            .all()
        )

    @staticmethod
    def gasto_por_pagamento(id_usuario):
        return (
            db.session.query(
                Assinatura.metodo_pagamento,
                func.coalesce(func.sum(_anualizado()), 0).label('total'),
                func.count(Assinatura.id_assinatura).label('qtd'),
            )
            .filter(
                Assinatura.id_usuario == id_usuario,
                Assinatura.status == 'ativa',
            )
            .group_by(Assinatura.metodo_pagamento)
            .all()
        )