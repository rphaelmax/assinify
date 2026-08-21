from app.models.usuario import Usuario
from app.exceptions import NotFoundError


class DeletarUsuarioService:
    @staticmethod
    def executar(id):
        usuario = Usuario.buscar_por_id(id)
        if usuario is None:
            raise NotFoundError('Usuário não encontrado')
        usuario.deletar()
