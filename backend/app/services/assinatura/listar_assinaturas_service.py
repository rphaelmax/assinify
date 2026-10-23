from app.models.assinatura import Assinatura
from app.extensions import db


# Campos permitidos para ordenação — evita SQL injection via query param
ORDENACAO_PERMITIDA = {
    'nome_servico': Assinatura.nome_servico,
    'valor_mensal': Assinatura.valor_mensal,
    'data_renovacao': Assinatura.data_renovacao,
    'status': Assinatura.status,
}


def _aplicar_filtros(query, filtros):
    """Aplica busca e filtros exatos sobre a query base, sem paginação/ordenação."""
    busca = (filtros.get('busca') or '').strip()
    if busca:
        query = query.filter(Assinatura.nome_servico.ilike(f'%{busca}%'))

    if filtros.get('id_categoria') is not None:
        try:
            id_cat = int(filtros['id_categoria'])
            if id_cat > 0:
                query = query.filter(Assinatura.id_categoria == id_cat)
        except (ValueError, TypeError):
            pass

    if filtros.get('status') in ('ativa', 'cancelada'):
        query = query.filter(Assinatura.status == filtros['status'])

    if filtros.get('metodo_pagamento'):
        mp = filtros['metodo_pagamento']
        if mp in ('cartao_credito', 'cartao_debito', 'pix', 'boleto', 'debito_automatico', 'transferencia', 'outro'):
            query = query.filter(Assinatura.metodo_pagamento == mp)

    if filtros.get('periodicidade') in ('semanal', 'mensal', 'anual'):
        query = query.filter(Assinatura.periodicidade == filtros['periodicidade'])

    return query


def _query_base(usuario_atual, filtros):
    query = Assinatura.query.filter_by(id_usuario=usuario_atual.id_usuario)
    return _aplicar_filtros(query, filtros or {})


class ListarAssinaturasService:
    """Lista assinaturas do usuário com busca, filtros, ordenação e paginação."""

    @staticmethod
    def construir_query(usuario_atual, filtros=None):
        """Expõe a query filtrada (sem ordenação/paginação) para reaproveitamento (ex.: exportação CSV)."""
        return _query_base(usuario_atual, filtros or {})

    @staticmethod
    def executar(usuario_atual, filtros=None):
        filtros = filtros or {}
        query = _query_base(usuario_atual, filtros)

        # Ordenação
        ordenar_por = filtros.get('ordenar_por') or 'data_renovacao'
        ordem = filtros.get('ordem') or 'asc'
        coluna = ORDENACAO_PERMITIDA.get(ordenar_por, Assinatura.data_renovacao)
        if ordem == 'desc':
            query = query.order_by(coluna.desc())
        else:
            query = query.order_by(coluna.asc())

        # Paginação opcional
        page_raw = filtros.get('page')
        limit_raw = filtros.get('limit')
        if page_raw is not None or limit_raw is not None:
            try:
                page = max(1, int(page_raw or 1))
            except (ValueError, TypeError):
                page = 1
            try:
                limit = int(limit_raw or 10)
                limit = max(1, min(100, limit))
            except (ValueError, TypeError):
                limit = 10

            total = query.count()
            total_paginas = max(1, (total + limit - 1) // limit)
            page = min(page, total_paginas)
            itens = query.offset((page - 1) * limit).limit(limit).all()
            return {
                'assinaturas': itens,
                'paginacao': {
                    'total': total,
                    'page': page,
                    'limit': limit,
                    'total_paginas': total_paginas
                }
            }

        return query.all()
