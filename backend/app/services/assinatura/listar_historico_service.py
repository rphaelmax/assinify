from app.models.assinatura import Assinatura
from app.repositories.historico_repository import HistoricoRepository
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

        return HistoricoRepository.listar_por_assinatura(id_assinatura)
