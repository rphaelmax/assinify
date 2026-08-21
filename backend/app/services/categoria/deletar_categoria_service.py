from app.models.categoria import Categoria
from app.exceptions import NotFoundError, ForbiddenError, ValidationError


class DeletarCategoriaService:
    @staticmethod
    def executar(id, id_usuario):
        categoria = Categoria.buscar_por_id(id)
        if categoria is None:
            raise NotFoundError('Categoria não encontrada')
        if categoria.id_usuario != id_usuario:
            raise ForbiddenError('Você só pode excluir suas próprias categorias')
        if categoria.assinaturas:
            raise ValidationError('Não é possível excluir uma categoria que possui assinaturas')
        categoria.deletar()