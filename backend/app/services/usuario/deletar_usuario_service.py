from app.models.usuario import Usuario
from app.repositories.usuario_repository import UsuarioRepository
from app.exceptions import NotFoundError, ForbiddenError


class DeletarUsuarioService:
    @staticmethod
    def executar(id, usuario_atual):
        usuario = Usuario.buscar_por_id(id)
        if usuario is None:
            raise NotFoundError('Usuário não encontrado')

        if UsuarioRepository.eh_admin_padrao(usuario):
            raise ForbiddenError('O admin padrão não pode ser excluído')

        if usuario.id_usuario == usuario_atual.id_usuario:
            raise ForbiddenError('Você não pode excluir a própria conta')

        usuario.deletar()