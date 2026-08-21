from app.models.usuario import Usuario
from app.exceptions import NotFoundError, ValidationError

ROLES_VALIDAS = ('user', 'admin')


class PromoverUsuarioService:
    @staticmethod
    def executar(id, nova_role):
        if nova_role not in ROLES_VALIDAS:
            raise ValidationError("Role inválida. Use 'user' ou 'admin'")

        usuario = Usuario.buscar_por_id(id)
        if usuario is None:
            raise NotFoundError('Usuário não encontrado')

        usuario.atualizar(role=nova_role)
        return usuario
