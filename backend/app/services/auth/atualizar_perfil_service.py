from app.models.usuario import Usuario
from app.repositories.usuario_repository import UsuarioRepository
from app.exceptions import ValidationError, ForbiddenError
from app.validacao import texto, validar_email


class AtualizarPerfilService:
    """Atualiza nome e email do próprio usuário autenticado."""

    @staticmethod
    def executar(dados, usuario_atual):
        nome = texto(dados['nome'], 'Nome', 100) if 'nome' in dados else None
        novo_email = None
        if 'email' in dados:
            novo_email = validar_email(dados['email'])
            if UsuarioRepository.eh_admin_padrao(usuario_atual) and novo_email != usuario_atual.email:
                raise ForbiddenError('O e-mail do admin padrão não pode ser alterado')
            if novo_email != usuario_atual.email:
                existente = UsuarioRepository.buscar_por_email(novo_email)
                if existente is not None:
                    raise ValidationError('Já existe um usuário cadastrado com esse email')

        usuario_atual.atualizar(nome=nome, email=novo_email)
        return usuario_atual
