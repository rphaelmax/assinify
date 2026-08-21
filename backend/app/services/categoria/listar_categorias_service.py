from app.models.categoria import Categoria


class ListarCategoriasService:
    @staticmethod
    def executar(id_usuario):
        """Cada usuário vê só as próprias categorias. Sem exceção para
        admin — admin não tem acesso automático às categorias de outros."""
        return Categoria.listar_por_usuario(id_usuario)