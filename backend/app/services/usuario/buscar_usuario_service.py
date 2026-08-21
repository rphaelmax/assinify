from app.models.usuario import Usuario
from app.exceptions import NotFoundError, ForbiddenError


class BuscarUsuarioService:
    @staticmethod
    def executar(id, usuario_atual):
        usuario = Usuario.buscar_por_id(id)
        if usuario is None:
            raise NotFoundError('Usuário não encontrado')

        if usuario_atual.role != 'admin' and usuario.id_usuario != usuario_atual.id_usuario:
            raise ForbiddenError('Você só pode acessar seus próprios dados')

        return usuario
