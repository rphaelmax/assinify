from app.models.assinatura import Assinatura
from app.exceptions import NotFoundError, ForbiddenError


class BuscarAssinaturaService:
    """Caso de uso: consultar uma assinatura acessível ao usuário."""

    @staticmethod
    def executar(id, usuario_atual):
        assinatura = Assinatura.buscar_por_id(id)
        if assinatura is None:
            raise NotFoundError('Assinatura não encontrada')

        if (
            usuario_atual.role != 'admin'
            and assinatura.id_usuario != usuario_atual.id_usuario
        ):
            raise ForbiddenError('Você só pode acessar suas próprias assinaturas')

        return assinatura
