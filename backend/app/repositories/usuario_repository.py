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
