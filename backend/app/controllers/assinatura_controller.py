from flask import Blueprint, request, jsonify, g, Response

from app.services.assinatura.criar_assinatura_service import CriarAssinaturaService
from app.services.assinatura.listar_assinaturas_service import ListarAssinaturasService
from app.services.assinatura.buscar_assinatura_service import BuscarAssinaturaService
from app.services.assinatura.atualizar_assinatura_service import AtualizarAssinaturaService
from app.services.assinatura.deletar_assinatura_service import DeletarAssinaturaService
from app.services.assinatura.estatisticas_assinatura_service import EstatisticasAssinaturaService
from app.services.assinatura.exportar_assinaturas_service import ExportarAssinaturasService
from app.services.assinatura.listar_historico_service import ListarHistoricoService
from app.services.assinatura.renovacoes_assinatura_service import RenovacoesAssinaturaService
from app.middlewares.auth_middleware import token_requerido

assinatura_bp = Blueprint('assinatura', __name__, url_prefix='/assinaturas')


def _montar_filtros():
    return {
        'busca': request.args.get('busca'),
        'id_categoria': request.args.get('id_categoria'),
        'status': request.args.get('status'),
        'metodo_pagamento': request.args.get('metodo_pagamento'),
        'periodicidade': request.args.get('periodicidade'),
        'ordenar_por': request.args.get('ordenar_por'),
        'ordem': request.args.get('ordem'),
        'page': request.args.get('page'),
        'limit': request.args.get('limit'),
    }


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
        filtros = _montar_filtros()
        resultado = ListarAssinaturasService.executar(g.usuario_atual, filtros)
        # Envelope paginado vs lista simples
        if isinstance(resultado, dict) and 'paginacao' in resultado:
            return jsonify({
                'assinaturas': [a.to_dict() for a in resultado['assinaturas']],
                'paginacao': resultado['paginacao']
            }), 200
        return jsonify([a.to_dict() for a in resultado]), 200

    @staticmethod
    @token_requerido
    def estatisticas():
        dados = EstatisticasAssinaturaService.executar(g.usuario_atual)
        return jsonify(dados), 200

    @staticmethod
    @token_requerido
    def proximas():
        itens = RenovacoesAssinaturaService.proximas(
            g.usuario_atual, request.args.get('limite')
        )
        return jsonify([a.to_dict() for a in itens]), 200

    @staticmethod
    @token_requerido
    def calendario():
        dados = RenovacoesAssinaturaService.calendario(
            g.usuario_atual, request.args.get('ano'), request.args.get('mes')
        )
        return jsonify(dados), 200

    @staticmethod
    @token_requerido
    def exportar():
        filtros = _montar_filtros()
        csv_text = ExportarAssinaturasService.executar(g.usuario_atual, filtros)
        # BOM para Excel reconhecer UTF-8
        body = '﻿' + csv_text
        return Response(
            body,
            mimetype='text/csv; charset=utf-8',
            headers={'Content-Disposition': 'attachment; filename="assinaturas.csv"'}
        )

    @staticmethod
    @token_requerido
    def historico(id):
        itens = ListarHistoricoService.executar(id, g.usuario_atual)
        return jsonify([h.to_dict() for h in itens]), 200

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


# IMPORTANTE: rotas literais devem vir ANTES de /<int:id> para não conflitar
assinatura_bp.add_url_rule('/estatisticas', view_func=AssinaturaController.estatisticas, methods=['GET'])
assinatura_bp.add_url_rule('/proximas', view_func=AssinaturaController.proximas, methods=['GET'])
assinatura_bp.add_url_rule('/calendario', view_func=AssinaturaController.calendario, methods=['GET'])
assinatura_bp.add_url_rule('/exportar', view_func=AssinaturaController.exportar, methods=['GET'])
assinatura_bp.add_url_rule('', view_func=AssinaturaController.criar, methods=['POST'])
assinatura_bp.add_url_rule('', view_func=AssinaturaController.listar, methods=['GET'])
assinatura_bp.add_url_rule('/<int:id>/historico', view_func=AssinaturaController.historico, methods=['GET'])
assinatura_bp.add_url_rule('/<int:id>', view_func=AssinaturaController.buscar, methods=['GET'])
assinatura_bp.add_url_rule('/<int:id>', view_func=AssinaturaController.atualizar, methods=['PUT'])
assinatura_bp.add_url_rule('/<int:id>', view_func=AssinaturaController.deletar, methods=['DELETE'])