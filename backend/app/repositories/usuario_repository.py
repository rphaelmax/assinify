from flask import current_app

from app.models.usuario import Usuario


class UsuarioRepository:
    """Consultas específicas de Usuario que não são CRUD convencional.

    O CRUD básico permanece encapsulado na própria Model, conforme a
    arquitetura definida para a disciplina.
    """

    @staticmethod
    def buscar_por_email(email):
        return Usuario.query.filter_by(email=email).first()

    @staticmethod
    def existe_admin():
        return Usuario.query.filter_by(role='admin').first() is not None

    @staticmethod
    def eh_admin_padrao(usuario):
        email_padrao = current_app.config['ADMIN_EMAIL'].strip().lower()
        return usuario.email.strip().lower() == email_padrao
