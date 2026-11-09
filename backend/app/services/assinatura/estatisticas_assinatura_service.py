from app.cambio import info as info_cambio
from app.moedas import MOEDA_PADRAO
from app.repositories.assinatura_repository import AssinaturaRepository


class EstatisticasAssinaturaService:
    """Agrega dados para os gráficos e cards do dashboard.

    Todos os valores são a parte do usuário (assinaturas divididas contam só a
    fração dele), anualizados e convertidos para a moeda base. Assinaturas em
    teste gratuito, pausadas e canceladas não entram nos totais de gasto.
    """

    @staticmethod
    def executar(usuario_atual):
        id_usuario = usuario_atual.id_usuario
        moeda_base = usuario_atual.moeda_base or MOEDA_PADRAO

        totais = AssinaturaRepository.totais(id_usuario, moeda_base)
        por_categoria = AssinaturaRepository.gasto_por_categoria(id_usuario, moeda_base)
        por_pagamento = AssinaturaRepository.gasto_por_pagamento(id_usuario, moeda_base)

        total_anual = totais['total_anual']
        total_ativas = totais['ativas']
        total_canceladas = totais['canceladas']
        total_mensal = float(total_anual) / 12 if total_anual else 0

        categoria_mais_cara = None
        if por_categoria:
            top = por_categoria[0]
            categoria_mais_cara = {
                'id_categoria': top.id_categoria,
                'nome_categoria': top.nome_categoria,
                'total_anual': float(top.total),
                'total_mensal': float(top.total) / 12,
                'qtd': top.qtd
            }

        media_anual = float(total_anual) / totais['cobrando'] if totais['cobrando'] else 0

        return {
            'moeda_base': moeda_base,
            'cambio': info_cambio(),
            'total_mensal': float(total_mensal),
            'total_anual': float(total_anual),
            'total_ativas': total_ativas,
            'total_em_teste': totais['em_teste'],
            'total_pausadas': totais['pausadas'],
            'total_canceladas': total_canceladas,
            'total_geral': total_ativas + totais['pausadas'] + total_canceladas,
            'media_anual': float(media_anual),
            'media_mensal': float(media_anual / 12) if media_anual else 0,
            'categoria_mais_cara': categoria_mais_cara,
            'por_categoria': [
                {
                    'id_categoria': r.id_categoria,
                    'nome_categoria': r.nome_categoria,
                    'total': float(r.total) / 12,
                    'total_anual': float(r.total),
                    'qtd': r.qtd,
                }
                for r in por_categoria
            ],
            'por_pagamento': [
                {'metodo': r.metodo_pagamento, 'total': float(r.total) / 12, 'total_anual': float(r.total), 'qtd': r.qtd}
                for r in por_pagamento
            ],
        }
