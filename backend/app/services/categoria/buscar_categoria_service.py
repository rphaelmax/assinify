from app.models.categoria import Categoria


class BuscarCategoriaService:
    @staticmethod
    def executar(id):
        categoria = Categoria.buscar_por_id(id)
        if categoria is None:
            raise ValueError('Categoria não encontrada')
        return categoria
