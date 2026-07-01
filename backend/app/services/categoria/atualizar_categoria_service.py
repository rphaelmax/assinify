from app.models.categoria import Categoria


class AtualizarCategoriaService:
    @staticmethod
    def executar(id, dados):
        categoria = Categoria.buscar_por_id(id)
        if categoria is None:
            raise ValueError('Categoria não encontrada')
        categoria.atualizar(
            nome_categoria=dados.get('nome_categoria'),
            descricao=dados.get('descricao')
        )
        return categoria
