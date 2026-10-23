from sqlalchemy import func, case
from app.extensions import db
from app.models.assinatura import Assinatura
from app.models.categoria import Categoria


def _anualizado_expr():
    """Expressão SQL que converte valor_mensal para valor anualizado segundo periodicidade."""
    return case(
        (Assinatura.periodicidade == 'semanal', Assinatura.valor_mensal * 52),
        (Assinatura.periodicidade == 'anual', Assinatura.valor_mensal * 1),
        else_=Assinatura.valor_mensal * 12
    )


class EstatisticasAssinaturaService:
    """Agrega dados para os gráficos e cards do dashboard (com anualização)."""

    @staticmethod
    def executar(usuario_atual):
        anualizado = _anualizado_expr()
        base = Assinatura.query.filter_by(id_usuario=usuario_atual.id_usuario)
        ativas = base.filter_by(status='ativa')

        total_anual = db.session.query(
            func.coalesce(func.sum(anualizado), 0)
        ).filter(
            Assinatura.id_usuario == usuario_atual.id_usuario,
            Assinatura.status == 'ativa'
        ).scalar()

        total_mensal = float(total_anual) / 12 if total_anual else 0

        total_ativas = ativas.count()
        total_canceladas = base.filter_by(status='cancelada').count()

        # Gasto por categoria (só ativas) — anualizado
        por_categoria = (
            db.session.query(
                Categoria.id_categoria,
                Categoria.nome_categoria,
                func.coalesce(func.sum(anualizado), 0).label('total'),
                func.count(Assinatura.id_assinatura).label('qtd'),
            )
            .join(Assinatura, Assinatura.id_categoria == Categoria.id_categoria)
            .filter(
                Assinatura.id_usuario == usuario_atual.id_usuario,
                Assinatura.status == 'ativa',
            )
            .group_by(Categoria.id_categoria, Categoria.nome_categoria)
            .order_by(func.sum(anualizado).desc())
            .all()
        )

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

        # Gasto por método de pagamento (só ativas) — anualizado
        por_pagamento = (
            db.session.query(
                Assinatura.metodo_pagamento,
                func.coalesce(func.sum(anualizado), 0).label('total'),
                func.count(Assinatura.id_assinatura).label('qtd'),
            )
            .filter(
                Assinatura.id_usuario == usuario_atual.id_usuario,
                Assinatura.status == 'ativa',
            )
            .group_by(Assinatura.metodo_pagamento)
            .all()
        )

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