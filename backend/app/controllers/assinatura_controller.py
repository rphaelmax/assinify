from flask import Blueprint, request, jsonify, g

from app.services.assinatura.criar_assinatura_service import CriarAssinaturaService
from app.services.assinatura.listar_assinaturas_service import ListarAssinaturasService
from app.services.assinatura.buscar_assinatura_service import BuscarAssinaturaService
from app.services.assinatura.atualizar_assinatura_service import AtualizarAssinaturaService
from app.services.assinatura.deletar_assinatura_service import DeletarAssinaturaService
from app.middlewares.auth_middleware import token_requerido

assinatura_bp = Blueprint('assinatura', __name__, url_prefix='/assinaturas')


class AssinaturaController:
    """Controller HTTP do recurso Assinatura."""

    @staticmethod
    @token_requerido
    def criar():
        dados = request.get_json() or {}
        assinatura = CriarAssinaturaService.executar(
            dados,
            g.usuario_atual
        )
        return jsonify(assinatura.to_dict()), 201

    @staticmethod
    @token_requerido
    def listar():
        assinaturas = ListarAssinaturasService.executar(g.usuario_atual)
        return jsonify([a.to_dict() for a in assinaturas]), 200

    @staticmethod
    @token_requerido
    def buscar(id):
        assinatura = BuscarAssinaturaService.executar(id, g.usuario_atual)
        return jsonify(assinatura.to_dict()), 200

    @staticmethod
    @token_requerido
    def atualizar(id):
        dados = request.get_json() or {}
        assinatura = AtualizarAssinaturaService.executar(
            id,
            dados,
            g.usuario_atual
        )
        return jsonify(assinatura.to_dict()), 200

    @staticmethod
    @token_requerido
    def deletar(id):
        DeletarAssinaturaService.executar(id, g.usuario_atual)
        return '', 204


assinatura_bp.add_url_rule('', view_func=AssinaturaController.criar, methods=['POST'])
assinatura_bp.add_url_rule('', view_func=AssinaturaController.listar, methods=['GET'])
assinatura_bp.add_url_rule('/<int:id>', view_func=AssinaturaController.buscar, methods=['GET'])
assinatura_bp.add_url_rule('/<int:id>', view_func=AssinaturaController.atualizar, methods=['PUT'])
assinatura_bp.add_url_rule('/<int:id>', view_func=AssinaturaController.deletar, methods=['DELETE'])
