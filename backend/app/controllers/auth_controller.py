from flask import Blueprint, request, jsonify, g

from app.services.auth.registrar_usuario_service import RegistrarUsuarioService
from app.services.auth.autenticar_usuario_service import AutenticarUsuarioService
from app.middlewares.auth_middleware import token_requerido


auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


class AuthController:
    """Controller responsável por receber requisições HTTP de autenticação.

    A Controller apenas extrai os dados da requisição, chama o Service do
    caso de uso e transforma o resultado em resposta HTTP.
    """

    @staticmethod
    def registrar():
        dados = request.get_json() or {}
        usuario = RegistrarUsuarioService.executar(dados)
        return jsonify(usuario.to_dict()), 201

    @staticmethod
    def login():
        dados = request.get_json() or {}
        token, usuario = AutenticarUsuarioService.executar(dados)
        return jsonify({'token': token, 'usuario': usuario.to_dict()}), 200

    @staticmethod
    @token_requerido
    def me():
        return jsonify(g.usuario_atual.to_dict()), 200


# As rotas são registradas a partir da classe Controller.
auth_bp.add_url_rule('/registrar', view_func=AuthController.registrar, methods=['POST'])
auth_bp.add_url_rule('/login', view_func=AuthController.login, methods=['POST'])
auth_bp.add_url_rule('/me', view_func=AuthController.me, methods=['GET'])
