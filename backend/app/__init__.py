from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy import inspect, text
from sqlalchemy.types import Float
from werkzeug.exceptions import HTTPException

from app.config import Config
from app.extensions import db
from app.exceptions import AppError, ValidationError

from app.controllers.auth_controller import auth_bp
from app.controllers.usuario_controller import usuario_bp
from app.controllers.categoria_controller import categoria_bp
from app.controllers.assinatura_controller import assinatura_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)
    db.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(usuario_bp)
    app.register_blueprint(categoria_bp)
    app.register_blueprint(assinatura_bp)

    @app.errorhandler(AppError)
    def tratar_erro_app(erro):
        return jsonify({'erro': erro.mensagem}), erro.status_code

    @app.errorhandler(HTTPException)
    def tratar_erro_http(erro):
        return jsonify({'erro': erro.description}), erro.code

    @app.errorhandler(Exception)
    def tratar_erro_inesperado(erro):
        db.session.rollback()
        app.logger.exception('Erro inesperado')
        return jsonify({'erro': 'Erro interno do servidor'}), 500

    @app.before_request
    def validar_corpo_json():
        if request.method not in ('POST', 'PUT', 'PATCH') or not request.is_json:
            return
        corpo = request.get_json(silent=True)
        if corpo is None and request.get_data():
            raise ValidationError('JSON inválido')
        if corpo is not None and not isinstance(corpo, dict):
            raise ValidationError('O corpo da requisição deve ser um objeto JSON')

    with app.app_context():
        _garantir_schema_atual()
        db.create_all()
        _garantir_admin_inicial(app)

    return app


def _garantir_schema_atual():
    """Aplica pequenas evoluções de schema sem apagar dados existentes."""
    inspector = inspect(db.engine)
    tabelas = inspector.get_table_names()

    if 'assinaturas' not in tabelas:
        return

    colunas = {coluna['name']: coluna['type'] for coluna in inspector.get_columns('assinaturas')}
    if 'metodo_pagamento' not in colunas:
        db.session.execute(text(
            "ALTER TABLE assinaturas ADD COLUMN metodo_pagamento "
            "VARCHAR(30) NOT NULL DEFAULT 'cartao_credito'"
        ))
        db.session.commit()

    if 'periodicidade' not in colunas:
        db.session.execute(text(
            "ALTER TABLE assinaturas ADD COLUMN periodicidade "
            "VARCHAR(20) NOT NULL DEFAULT 'mensal'"
        ))
        db.session.commit()

    if db.engine.dialect.name == 'mysql' and isinstance(colunas['valor_mensal'], Float):
        db.session.execute(text(
            "alter table assinaturas modify valor_mensal decimal(10,2) not null"
        ))
        db.session.commit()


def _garantir_admin_inicial(app):
    """Cria um usuário admin no primeiro startup, caso nenhum exista.
    Necessário porque a promoção a admin (rota /usuarios/<id>/role) é
    restrita a admins — precisa existir um primeiro admin de algum jeito."""
    from app.repositories.usuario_repository import UsuarioRepository
    from app.models.usuario import Usuario
    from app.security.senha import hashear_senha

    if UsuarioRepository.existe_admin():
        return

    admin = Usuario(
        nome='Administrador',
        email=app.config['ADMIN_EMAIL'],
        senha_hash=hashear_senha(app.config['ADMIN_SENHA']),
        role='admin'
    )
    admin.salvar()