from app.models.usuario import Usuario
from app.repositories.usuario_repository import UsuarioRepository
from app.exceptions import NotFoundError, ValidationError, ForbiddenError

ROLES_VALIDAS = ('user', 'admin')


class PromoverUsuarioService:
    @staticmethod
    def executar(id, nova_role, usuario_atual):
        if nova_role not in ROLES_VALIDAS:
            raise ValidationError("Role inválida. Use 'user' ou 'admin'")

        usuario = Usuario.buscar_por_id(id)
        if usuario is None:
            raise NotFoundError('Usuário não encontrado')

        if UsuarioRepository.eh_admin_padrao(usuario):
            raise ForbiddenError('A role do admin padrão não pode ser alterada')

        if usuario.id_usuario == usuario_atual.id_usuario:
            raise ForbiddenError('Você não pode alterar a própria role')

        usuario.atualizar(role=nova_role)
        return usuario