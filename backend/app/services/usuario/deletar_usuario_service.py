from app.models.usuario import Usuario


class DeletarUsuarioService:
    @staticmethod
    def executar(id):
        usuario = Usuario.buscar_por_id(id)
        if usuario is None:
            raise ValueError('Usuário não encontrado')
        usuario.deletar()
