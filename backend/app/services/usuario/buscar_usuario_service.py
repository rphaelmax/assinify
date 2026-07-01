from app.models.usuario import Usuario


class BuscarUsuarioService:
    @staticmethod
    def executar(id):
        usuario = Usuario.buscar_por_id(id)
        if usuario is None:
            raise ValueError('Usuário não encontrado')
        return usuario
