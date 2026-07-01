from flask import request, jsonify
from app.services.usuario.criar_usuario_service import CriarUsuarioService
from app.services.usuario.listar_usuarios_service import ListarUsuariosService
from app.services.usuario.buscar_usuario_service import BuscarUsuarioService
from app.services.usuario.atualizar_usuario_service import AtualizarUsuarioService
from app.services.usuario.deletar_usuario_service import DeletarUsuarioService


class UsuarioController:
    @staticmethod
    def criar():
        try:
            dados = request.get_json()
            usuario = CriarUsuarioService.executar(dados)
            return jsonify(usuario.to_dict()), 201
        except ValueError as e:
            return jsonify({'erro': str(e)}), 400

    @staticmethod
    def listar():
        usuarios = ListarUsuariosService.executar()
        return jsonify([u.to_dict() for u in usuarios]), 200

    @staticmethod
    def buscar(id):
        try:
            usuario = BuscarUsuarioService.executar(id)
            return jsonify(usuario.to_dict()), 200
        except ValueError as e:
            return jsonify({'erro': str(e)}), 404

    @staticmethod
    def atualizar(id):
        try:
            dados = request.get_json()
            usuario = AtualizarUsuarioService.executar(id, dados)
            return jsonify(usuario.to_dict()), 200
        except ValueError as e:
            return jsonify({'erro': str(e)}), 404

    @staticmethod
    def deletar(id):
        try:
            DeletarUsuarioService.executar(id)
            return '', 204
        except ValueError as e:
            return jsonify({'erro': str(e)}), 404
