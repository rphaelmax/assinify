from app.models.usuario import Usuario
from app.repositories.usuario_repository import UsuarioRepository
from app.exceptions import ValidationError, ForbiddenError
from app.validacao import texto, validar_email, validar_moeda


class AtualizarPerfilService:
    """Atualiza nome, email e moeda base do próprio usuário autenticado."""

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

        moeda_base = validar_moeda(dados['moeda_base']) if 'moeda_base' in dados else None

        usuario_atual.atualizar(nome=nome, email=novo_email, moeda_base=moeda_base)
        return usuario_atual
