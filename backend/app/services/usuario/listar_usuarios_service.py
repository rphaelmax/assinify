from app.models.usuario import Usuario


class ListarUsuariosService:
    @staticmethod
    def executar():
        return Usuario.listar_todos()
