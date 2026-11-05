from app.models.categoria import Categoria

class CategoriaRepository:
    """Consultas de Categoria que vão além do CRUD básico (que fica na Model)."""

    @staticmethod
    def nomes_por_ids(ids):
        """Mapa {id_categoria: nome_categoria} em uma única consulta."""
        if not ids:
            return {}
        categorias = Categoria.query.filter(Categoria.id_categoria.in_(ids)).all()
        return {c.id_categoria: c.nome_categoria for c in categorias}