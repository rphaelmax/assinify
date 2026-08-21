from app.repositories.usuario_repository import UsuarioRepository
from app.security.senha import verificar_senha
from app.security.token import gerar_token
from app.exceptions import ValidationError, UnauthorizedError


class AutenticarUsuarioService:
    @staticmethod
    def executar(dados):
        email = dados.get('email')
        senha = dados.get('senha')

        if not email or not senha:
            raise ValidationError('Email e senha são obrigatórios')

        usuario = UsuarioRepository.buscar_por_email(email)
        if usuario is None or not verificar_senha(senha, usuario.senha_hash):
            raise UnauthorizedError('Email ou senha inválidos')

        token = gerar_token(usuario.id_usuario, usuario.role)
        return token, usuario
