from functools import wraps

import jwt
from flask import request, g

from app.security.token import decodificar_token
from app.models.usuario import Usuario
from app.exceptions import UnauthorizedError, ForbiddenError


def token_requerido(f):
    """Exige um JWT válido no header Authorization e disponibiliza o
    usuário autenticado em g.usuario_atual para a view decorada."""

    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            raise UnauthorizedError('Token não fornecido')

        token = auth_header.split(' ', 1)[1].strip()

        try:
            payload = decodificar_token(token)
        except jwt.ExpiredSignatureError:
            raise UnauthorizedError('Token expirado')
        except jwt.InvalidTokenError:
            raise UnauthorizedError('Token inválido')

        usuario = Usuario.buscar_por_id(payload['id_usuario'])
        if usuario is None:
            raise UnauthorizedError('Usuário do token não existe mais')

        g.usuario_atual = usuario
        return f(*args, **kwargs)

    return wrapper


def admin_requerido(f):
    """Exige que g.usuario_atual (já definido por token_requerido) tenha
    role='admin'. Deve ser usado sempre abaixo de @token_requerido."""

    @wraps(f)
    def wrapper(*args, **kwargs):
        if g.usuario_atual.role != 'admin':
            raise ForbiddenError('Acesso restrito a administradores')
        return f(*args, **kwargs)

    return wrapper
