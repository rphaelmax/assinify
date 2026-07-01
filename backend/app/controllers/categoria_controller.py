from flask import request, jsonify
from app.services.categoria.criar_categoria_service import CriarCategoriaService
from app.services.categoria.listar_categorias_service import ListarCategoriasService
from app.services.categoria.buscar_categoria_service import BuscarCategoriaService
from app.services.categoria.atualizar_categoria_service import AtualizarCategoriaService
from app.services.categoria.deletar_categoria_service import DeletarCategoriaService


class CategoriaController:
    @staticmethod
    def criar():
        try:
            dados = request.get_json()
            categoria = CriarCategoriaService.executar(dados)
            return jsonify(categoria.to_dict()), 201
        except ValueError as e:
            return jsonify({'erro': str(e)}), 400

    @staticmethod
    def listar():
        categorias = ListarCategoriasService.executar()
        return jsonify([c.to_dict() for c in categorias]), 200

    @staticmethod
    def buscar(id):
        try:
            categoria = BuscarCategoriaService.executar(id)
            return jsonify(categoria.to_dict()), 200
        except ValueError as e:
            return jsonify({'erro': str(e)}), 404

    @staticmethod
    def atualizar(id):
        try:
            dados = request.get_json()
            categoria = AtualizarCategoriaService.executar(id, dados)
            return jsonify(categoria.to_dict()), 200
        except ValueError as e:
            return jsonify({'erro': str(e)}), 404

    @staticmethod
    def deletar(id):
        try:
            DeletarCategoriaService.executar(id)
            return '', 204
        except ValueError as e:
            return jsonify({'erro': str(e)}), 404
