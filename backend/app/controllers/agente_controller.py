from flask import Blueprint, request, jsonify, g

from app.services.agente.conversar_agente_service import ConversarAgenteService
from app.services.agente.gerar_insights_service import GerarInsightsService
from app.services.agente.recomendar_planos_service import RecomendarPlanosService
from app.middlewares.auth_middleware import token_requerido

agente_bp = Blueprint('agente', __name__, url_prefix='/agente')


class AgenteController:
    """Controller HTTP do agente de IA."""

    @staticmethod
    @token_requerido
    def conversar():
        dados = request.get_json() or {}
        return jsonify(ConversarAgenteService.executar(dados, g.usuario_atual)), 200

    @staticmethod
    @token_requerido
    def insights():
        forcar = request.args.get('atualizar') == '1'
        return jsonify(GerarInsightsService.executar(g.usuario_atual, forcar)), 200

    @staticmethod
    @token_requerido
    def planos():
        dados = request.get_json(silent=True) or {}
        return jsonify(RecomendarPlanosService.executar(g.usuario_atual, dados.get('id_assinatura'))), 200


agente_bp.add_url_rule('', view_func=AgenteController.conversar, methods=['POST'])
agente_bp.add_url_rule('/insights', view_func=AgenteController.insights, methods=['GET'])
agente_bp.add_url_rule('/planos', view_func=AgenteController.planos, methods=['POST'])
