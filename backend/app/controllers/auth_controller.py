from flask import Blueprint, request, jsonify, g

from app.services.auth.registrar_usuario_service import RegistrarUsuarioService
from app.services.auth.autenticar_usuario_service import AutenticarUsuarioService
from app.services.auth.atualizar_perfil_service import AtualizarPerfilService
from app.services.auth.alterar_senha_service import AlterarSenhaService
from app.middlewares.auth_middleware import token_requerido


auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


class AuthController:
    """Controller responsável por receber requisições HTTP de autenticação."""

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

    @staticmethod
    @token_requerido
    def atualizar_perfil():
        dados = request.get_json() or {}
        usuario = AtualizarPerfilService.executar(dados, g.usuario_atual)
        return jsonify(usuario.to_dict()), 200

    @staticmethod
    @token_requerido
    def alterar_senha():
        dados = request.get_json() or {}
        AlterarSenhaService.executar(dados, g.usuario_atual)
        return jsonify({'mensagem': 'Senha alterada com sucesso'}), 200


auth_bp.add_url_rule('/registrar', view_func=AuthController.registrar, methods=['POST'])
auth_bp.add_url_rule('/login', view_func=AuthController.login, methods=['POST'])
auth_bp.add_url_rule('/me', view_func=AuthController.me, methods=['GET'])
auth_bp.add_url_rule('/perfil', view_func=AuthController.atualizar_perfil, methods=['PUT'])
auth_bp.add_url_rule('/senha', view_func=AuthController.alterar_senha, methods=['PATCH'])
