import jwt
from datetime import datetime, timedelta, timezone
from flask import current_app

EXPIRACAO_HORAS = 8


def gerar_token(id_usuario, role):
    payload = {
        'id_usuario': id_usuario,
        'role': role,
        'exp': datetime.now(timezone.utc) + timedelta(hours=EXPIRACAO_HORAS)
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')


def decodificar_token(token):
    return jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
