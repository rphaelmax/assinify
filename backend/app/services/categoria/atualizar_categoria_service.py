from app.models.categoria import Categoria
from app.exceptions import NotFoundError, ForbiddenError, ValidationError


class AtualizarCategoriaService:
    @staticmethod
    def executar(id, dados, id_usuario):
        categoria = Categoria.buscar_por_id(id)
        if categoria is None:
            raise NotFoundError('Categoria não encontrada')
        if categoria.id_usuario != id_usuario:
            raise ForbiddenError('Você só pode alterar suas próprias categorias')
        if 'nome_categoria' in dados and not dados.get('nome_categoria'):
            raise ValidationError('Nome da categoria é obrigatório')
        categoria.atualizar(
            nome_categoria=dados.get('nome_categoria'),
            descricao=dados.get('descricao')
        )
        return categoria