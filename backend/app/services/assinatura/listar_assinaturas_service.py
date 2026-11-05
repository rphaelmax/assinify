from app.repositories.assinatura_repository import AssinaturaRepository
from app.services.assinatura.criar_assinatura_service import METODOS_PAGAMENTO


def normalizar_filtros(filtros):
    """Valida os filtros recebidos da query string e devolve só critérios seguros.
    Valores inválidos são ignorados (equivalem a 'sem filtro')."""
    filtros = filtros or {}
    criterios = {}

    busca = (filtros.get('busca') or '').strip()
    if busca:
        criterios['busca'] = busca

    try:
        id_categoria = int(filtros['id_categoria']) if filtros.get('id_categoria') is not None else 0
        if id_categoria > 0:
            criterios['id_categoria'] = id_categoria
    except (ValueError, TypeError):
        pass

    if filtros.get('status') in ('ativa', 'cancelada'):
        criterios['status'] = filtros['status']

    if filtros.get('metodo_pagamento') in METODOS_PAGAMENTO:
        criterios['metodo_pagamento'] = filtros['metodo_pagamento']

    if filtros.get('periodicidade') in ('semanal', 'mensal', 'anual'):
        criterios['periodicidade'] = filtros['periodicidade']

    return criterios


class ListarAssinaturasService:
    """Lista assinaturas do usuário com busca, filtros, ordenação e paginação."""

    @staticmethod
    def executar(usuario_atual, filtros=None):
        filtros = filtros or {}
        id_usuario = usuario_atual.id_usuario
        criterios = normalizar_filtros(filtros)
        ordenar_por = filtros.get('ordenar_por')
        ordem = filtros.get('ordem')

        page_raw = filtros.get('page')
        limit_raw = filtros.get('limit')

        # Sem paginação: devolve a lista completa
        if page_raw is None and limit_raw is None:
            return AssinaturaRepository.listar_filtradas(id_usuario, criterios, ordenar_por, ordem)

        try:
            page = max(1, int(page_raw or 1))
        except (ValueError, TypeError):
            page = 1
        try:
            limit = max(1, min(100, int(limit_raw or 10)))
        except (ValueError, TypeError):
            limit = 10

        total = AssinaturaRepository.contar_filtradas(id_usuario, criterios)
        total_paginas = max(1, (total + limit - 1) // limit)
        page = min(page, total_paginas)

        itens = AssinaturaRepository.listar_filtradas(
            id_usuario, criterios, ordenar_por, ordem,
            offset=(page - 1) * limit, limit=limit
        )
        return {
            'assinaturas': itens,
            'paginacao': {
                'total': total,
                'page': page,
                'limit': limit,
                'total_paginas': total_paginas
            }
        }