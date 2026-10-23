from app.models.usuario import Usuario
from app.repositories.usuario_repository import UsuarioRepository
from app.exceptions import NotFoundError, ValidationError, ForbiddenError
from app.validacao import texto, validar_email


class AtualizarUsuarioService:
    """Caso de uso: atualizar nome e email do usuário."""

    @staticmethod
    def executar(id, dados, usuario_atual):
        usuario = Usuario.buscar_por_id(id)
        if usuario is None:
            raise NotFoundError('Usuário não encontrado')

        if usuario_atual.role != 'admin' and usuario.id_usuario != usuario_atual.id_usuario:
            raise ForbiddenError('Você só pode alterar seus próprios dados')

        novo_email = validar_email(dados['email']) if 'email' in dados else None

        if UsuarioRepository.eh_admin_padrao(usuario):
            if usuario.id_usuario != usuario_atual.id_usuario:
                raise ForbiddenError('O admin padrão não pode ser editado por outros usuários')
            if novo_email and novo_email != usuario.email:
                raise ForbiddenError('O e-mail do admin padrão não pode ser alterado')

        nome = texto(dados['nome'], 'Nome', 100) if 'nome' in dados else None

        if novo_email and novo_email != usuario.email:
            existente = UsuarioRepository.buscar_por_email(novo_email)
            if existente is not None:
                raise ValidationError('Já existe um usuário cadastrado com esse email')

        usuario.atualizar(
            nome=nome,
            email=novo_email
        )
        return usuario