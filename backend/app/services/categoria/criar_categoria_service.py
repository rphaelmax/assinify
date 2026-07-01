from app.models.categoria import Categoria


class CriarCategoriaService:
    @staticmethod
    def executar(dados):
        if not dados.get('nome_categoria'):
            raise ValueError('Nome da categoria é obrigatório')
        categoria = Categoria(
            nome_categoria=dados['nome_categoria'],
            descricao=dados.get('descricao')
        )
        categoria.salvar()
        return categoria
