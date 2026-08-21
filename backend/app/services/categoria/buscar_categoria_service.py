from app.models.categoria import Categoria
from app.exceptions import NotFoundError, ForbiddenError


class BuscarCategoriaService:
    @staticmethod
    def executar(id, id_usuario):
        categoria = Categoria.buscar_por_id(id)
        if categoria is None:
            raise NotFoundError('Categoria não encontrada')
        if categoria.id_usuario != id_usuario:
            raise ForbiddenError('Você só pode acessar suas próprias categorias')
        return categoria