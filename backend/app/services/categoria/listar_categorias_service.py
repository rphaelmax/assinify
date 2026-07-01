from app.models.categoria import Categoria


class ListarCategoriasService:
    @staticmethod
    def executar():
        return Categoria.listar_todos()
