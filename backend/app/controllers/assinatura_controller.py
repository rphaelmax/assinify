from flask import request, jsonify
from app.services.assinatura.criar_assinatura_service import CriarAssinaturaService
from app.services.assinatura.listar_assinaturas_service import ListarAssinaturasService
from app.services.assinatura.buscar_assinatura_service import BuscarAssinaturaService
from app.services.assinatura.atualizar_assinatura_service import AtualizarAssinaturaService
from app.services.assinatura.deletar_assinatura_service import DeletarAssinaturaService


class AssinaturaController:
    @staticmethod
    def criar():
        try:
            dados = request.get_json()
            assinatura = CriarAssinaturaService.executar(dados)
            return jsonify(assinatura.to_dict()), 201
        except ValueError as e:
            return jsonify({'erro': str(e)}), 400

    @staticmethod
    def listar():
        assinaturas = ListarAssinaturasService.executar()
        return jsonify([a.to_dict() for a in assinaturas]), 200

    @staticmethod
    def buscar(id):
        try:
            assinatura = BuscarAssinaturaService.executar(id)
            return jsonify(assinatura.to_dict()), 200
        except ValueError as e:
            return jsonify({'erro': str(e)}), 404

    @staticmethod
    def atualizar(id):
        try:
            dados = request.get_json()
            assinatura = AtualizarAssinaturaService.executar(id, dados)
            return jsonify(assinatura.to_dict()), 200
        except ValueError as e:
            return jsonify({'erro': str(e)}), 404

    @staticmethod
    def deletar(id):
        try:
            DeletarAssinaturaService.executar(id)
            return '', 204
        except ValueError as e:
            return jsonify({'erro': str(e)}), 404
