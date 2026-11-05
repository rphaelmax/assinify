import csv
import io

from app.repositories.assinatura_repository import AssinaturaRepository
from app.repositories.categoria_repository import CategoriaRepository
from app.services.assinatura.listar_assinaturas_service import normalizar_filtros


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
        filtros = filtros or {}
        # Exporta tudo que passou pelos filtros (page/limit são ignorados)
        assinaturas = AssinaturaRepository.listar_filtradas(
            usuario_atual.id_usuario,
            normalizar_filtros(filtros),
            filtros.get('ordenar_por'),
            filtros.get('ordem')
        )

        # Mapa id_categoria -> nome em uma única consulta (evita N+1)
        cat_map = CategoriaRepository.nomes_por_ids({a.id_categoria for a in assinaturas})

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
