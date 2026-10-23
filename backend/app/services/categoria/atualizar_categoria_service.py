from app.models.categoria import Categoria
from app.exceptions import NotFoundError, ForbiddenError
from app.validacao import texto

class AtualizarCategoriaService:
    @staticmethod
    def executar(id, dados, id_usuario):
        categoria = Categoria.buscar_por_id(id)
        if categoria is None:
            raise NotFoundError('Categoria não encontrada')
        if categoria.id_usuario != id_usuario:
            raise ForbiddenError('Você só pode alterar suas próprias categorias')
        nome_categoria = texto(dados['nome_categoria'], 'Nome da categoria', 100) if 'nome_categoria' in dados else None
        descricao = texto(dados['descricao'], 'Descrição', 255, obrigatorio=False) if 'descricao' in dados else None
        categoria.atualizar(
            nome_categoria=nome_categoria,
            descricao=descricao
        )
        return categoria