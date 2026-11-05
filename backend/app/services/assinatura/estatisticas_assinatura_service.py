from app.repositories.assinatura_repository import AssinaturaRepository


class EstatisticasAssinaturaService:
    """Agrega dados para os gráficos e cards do dashboard (com anualização)."""

    @staticmethod
    def executar(usuario_atual):
        id_usuario = usuario_atual.id_usuario

        totais = AssinaturaRepository.totais(id_usuario)
        por_categoria = AssinaturaRepository.gasto_por_categoria(id_usuario)
        por_pagamento = AssinaturaRepository.gasto_por_pagamento(id_usuario)

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

        media_anual = float(total_anual) / total_ativas if total_ativas else 0

        return {
            'total_mensal': float(total_mensal),
            'total_anual': float(total_anual),
            'total_ativas': total_ativas,
            'total_canceladas': total_canceladas,
            'total_geral': total_ativas + total_canceladas,
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