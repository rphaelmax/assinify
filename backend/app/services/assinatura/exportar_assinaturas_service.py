import csv
import io

from app.services.assinatura.listar_assinaturas_service import ListarAssinaturasService


CABECALHO_CSV = [
    'Nome do serviço',
    'Valor mensal (R$)',
    'Periodicidade',
    'Valor anualizado (R$)',
    'Data de renovação',
    'Status',
    'Plano',
    'Método de pagamento',
    'Categoria'
]


class ExportarAssinaturasService:
    """Gera CSV das assinaturas filtradas do usuário (sem dependências externas)."""

    @staticmethod
    def executar(usuario_atual, filtros=None):
        from app.models.categoria import Categoria

        filtros = filtros or {}
        # Remove paginação para exportar tudo que passou pelos filtros
        filtros_export = {k: v for k, v in filtros.items() if k not in ('page', 'limit')}

        query = ListarAssinaturasService.construir_query(usuario_atual, filtros_export)

        # Ordenação (igual ao listar)
        from app.services.assinatura.listar_assinaturas_service import ORDENACAO_PERMITIDA
        from app.models.assinatura import Assinatura
        ordenar_por = filtros_export.get('ordenar_por') or 'data_renovacao'
        ordem = filtros_export.get('ordem') or 'asc'
        coluna = ORDENACAO_PERMITIDA.get(ordenar_por, Assinatura.data_renovacao)
        query = query.order_by(coluna.desc() if ordem == 'desc' else coluna.asc())

        assinaturas = query.all()

        # Mapa id_categoria -> nome para evitar N+1 quando possível
        cat_map = {}
        if assinaturas:
            ids = {a.id_categoria for a in assinaturas}
            for c in Categoria.query.filter(Categoria.id_categoria.in_(ids)).all():
                cat_map[c.id_categoria] = c.nome_categoria

        buf = io.StringIO()
        writer = csv.writer(buf, quoting=csv.QUOTE_MINIMAL, lineterminator='\r\n')
        writer.writerow(CABECALHO_CSV)
        for a in assinaturas:
            writer.writerow([
                a.nome_servico,
                f'{float(a.valor_mensal):.2f}',
                a.periodicidade or 'mensal',
                f'{float(a.valor_anualizado):.2f}',
                a.data_renovacao.isoformat() if a.data_renovacao else '',
                a.status,
                a.tipo_plano or '',
                a.metodo_pagamento or '',
                cat_map.get(a.id_categoria, '')
            ])
        return buf.getvalue()
