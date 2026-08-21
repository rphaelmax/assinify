from flask import Blueprint, request, jsonify, g

from app.services.categoria.criar_categoria_service import CriarCategoriaService
from app.services.categoria.listar_categorias_service import ListarCategoriasService
from app.services.categoria.buscar_categoria_service import BuscarCategoriaService
from app.services.categoria.atualizar_categoria_service import AtualizarCategoriaService
from app.services.categoria.deletar_categoria_service import DeletarCategoriaService
from app.middlewares.auth_middleware import token_requerido

categoria_bp = Blueprint('categoria', __name__, url_prefix='/categorias')


class CategoriaController:
    """Controller HTTP do recurso Categoria."""

    @staticmethod
    @token_requerido
    def criar():
        dados = request.get_json() or {}
        categoria = CriarCategoriaService.executar(
            dados,
            g.usuario_atual.id_usuario
        )
        return jsonify(categoria.to_dict()), 201

    @staticmethod
    @token_requerido
    def listar():
        categorias = ListarCategoriasService.executar(g.usuario_atual.id_usuario)
        return jsonify([c.to_dict() for c in categorias]), 200

    @staticmethod
    @token_requerido
    def buscar(id):
        categoria = BuscarCategoriaService.executar(id, g.usuario_atual.id_usuario)
        return jsonify(categoria.to_dict()), 200

    @staticmethod
    @token_requerido
    def atualizar(id):
        dados = request.get_json() or {}
        categoria = AtualizarCategoriaService.executar(
            id,
            dados,
            g.usuario_atual.id_usuario
        )
        return jsonify(categoria.to_dict()), 200

    @staticmethod
    @token_requerido
    def deletar(id):
        DeletarCategoriaService.executar(id, g.usuario_atual.id_usuario)
        return '', 204


categoria_bp.add_url_rule('', view_func=CategoriaController.criar, methods=['POST'])
categoria_bp.add_url_rule('', view_func=CategoriaController.listar, methods=['GET'])
categoria_bp.add_url_rule('/<int:id>', view_func=CategoriaController.buscar, methods=['GET'])
categoria_bp.add_url_rule('/<int:id>', view_func=CategoriaController.atualizar, methods=['PUT'])
categoria_bp.add_url_rule('/<int:id>', view_func=CategoriaController.deletar, methods=['DELETE'])
