from flask import Blueprint, request, jsonify, g

from app.services.usuario.listar_usuarios_service import ListarUsuariosService
from app.services.usuario.buscar_usuario_service import BuscarUsuarioService
from app.services.usuario.atualizar_usuario_service import AtualizarUsuarioService
from app.services.usuario.deletar_usuario_service import DeletarUsuarioService
from app.services.usuario.promover_usuario_service import PromoverUsuarioService
from app.middlewares.auth_middleware import token_requerido, admin_requerido

usuario_bp = Blueprint('usuario', __name__, url_prefix='/usuarios')


class UsuarioController:
    """Controller HTTP do recurso Usuario."""

    @staticmethod
    @token_requerido
    @admin_requerido
    def listar():
        usuarios = ListarUsuariosService.executar()
        return jsonify([u.to_dict() for u in usuarios]), 200

    @staticmethod
    @token_requerido
    def buscar(id):
        usuario = BuscarUsuarioService.executar(id, g.usuario_atual)
        return jsonify(usuario.to_dict()), 200

    @staticmethod
    @token_requerido
    def atualizar(id):
        dados = request.get_json() or {}
        usuario = AtualizarUsuarioService.executar(id, dados, g.usuario_atual)
        return jsonify(usuario.to_dict()), 200

    @staticmethod
    @token_requerido
    @admin_requerido
    def deletar(id):
        DeletarUsuarioService.executar(id)
        return '', 204

    @staticmethod
    @token_requerido
    @admin_requerido
    def promover(id):
        dados = request.get_json() or {}
        usuario = PromoverUsuarioService.executar(id, dados.get('role'))
        return jsonify(usuario.to_dict()), 200


usuario_bp.add_url_rule('', view_func=UsuarioController.listar, methods=['GET'])
usuario_bp.add_url_rule('/<int:id>', view_func=UsuarioController.buscar, methods=['GET'])
usuario_bp.add_url_rule('/<int:id>', view_func=UsuarioController.atualizar, methods=['PUT'])
usuario_bp.add_url_rule('/<int:id>', view_func=UsuarioController.deletar, methods=['DELETE'])
usuario_bp.add_url_rule('/<int:id>/role', view_func=UsuarioController.promover, methods=['PATCH'])
