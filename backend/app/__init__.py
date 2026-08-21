from flask import Flask, jsonify
from flask_cors import CORS
from sqlalchemy import inspect, text

from app.config import Config
from app.extensions import db
from app.exceptions import AppError

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

    colunas = {coluna['name'] for coluna in inspector.get_columns('assinaturas')}
    if 'metodo_pagamento' not in colunas:
        db.session.execute(text(
            "ALTER TABLE assinaturas ADD COLUMN metodo_pagamento "
            "VARCHAR(30) NOT NULL DEFAULT 'cartao_credito'"
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
