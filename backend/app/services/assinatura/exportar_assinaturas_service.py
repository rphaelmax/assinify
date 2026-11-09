import csv
import io

from app.repositories.assinatura_repository import AssinaturaRepository
from app.repositories.categoria_repository import CategoriaRepository
from app.services.assinatura.listar_assinaturas_service import normalizar_filtros


CABECALHO_CSV = [
    'Nome do serviço',
    'Valor por período',
    'Moeda',
    'Dividido entre (pessoas)',
    'Periodicidade',
    'Sua parte anual (moeda base)',
    'Moeda base',
    'Data de renovação',
    'Status',
    'Data de cancelamento',
    'Fim do teste',
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
        moeda_base = usuario_atual.moeda_base or 'BRL'
        for a in assinaturas:
            writer.writerow([
                a.nome_servico,
                f'{float(a.valor_mensal):.2f}',
                a.moeda,
                a.pessoas,
                a.periodicidade or 'mensal',
                f'{float(a.anualizado_em(moeda_base)):.2f}',
                moeda_base,
                a.data_renovacao.isoformat() if a.data_renovacao else '',
                a.status,
                a.data_cancelamento.isoformat() if a.data_cancelamento else '',
                a.teste_ate.isoformat() if a.teste_ate else '',
                a.tipo_plano or '',
                a.metodo_pagamento or '',
                cat_map.get(a.id_categoria, '')
            ])
        return buf.getvalue()
