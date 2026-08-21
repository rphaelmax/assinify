from app.models.usuario import Usuario
from app.repositories.usuario_repository import UsuarioRepository
from app.exceptions import NotFoundError, ValidationError, ForbiddenError


class AtualizarUsuarioService:
    """Caso de uso: atualizar nome e email do usuário."""

    @staticmethod
    def executar(id, dados, usuario_atual):
        usuario = Usuario.buscar_por_id(id)
        if usuario is None:
            raise NotFoundError('Usuário não encontrado')

        if usuario_atual.role != 'admin' and usuario.id_usuario != usuario_atual.id_usuario:
            raise ForbiddenError('Você só pode alterar seus próprios dados')

        if 'nome' in dados and not dados.get('nome'):
            raise ValidationError('Nome é obrigatório')

        novo_email = dados.get('email')
        if novo_email and novo_email != usuario.email:
            existente = UsuarioRepository.buscar_por_email(novo_email)
            if existente is not None:
                raise ValidationError('Já existe um usuário cadastrado com esse email')

        usuario.atualizar(
            nome=dados.get('nome'),
            email=novo_email
        )
        return usuario
