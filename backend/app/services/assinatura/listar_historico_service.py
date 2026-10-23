from app.models.assinatura import Assinatura
from app.models.historico_assinatura import HistoricoAssinatura
from app.exceptions import NotFoundError, ForbiddenError


class ListarHistoricoService:
    """Lista o histórico de alterações de uma assinatura do usuário."""

    @staticmethod
    def executar(id_assinatura, usuario_atual):
        assinatura = Assinatura.buscar_por_id(id_assinatura)
        if assinatura is None:
            raise NotFoundError('Assinatura não encontrada')
        if usuario_atual.role != 'admin' and assinatura.id_usuario != usuario_atual.id_usuario:
            raise ForbiddenError('Você só pode ver o histórico das suas próprias assinaturas')

        return (
            HistoricoAssinatura.query
            .filter_by(id_assinatura=id_assinatura)
            .order_by(HistoricoAssinatura.data_alteracao.desc())
            .all()
        )
