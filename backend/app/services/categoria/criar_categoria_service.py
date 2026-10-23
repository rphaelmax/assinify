from app.models.categoria import Categoria
from app.validacao import texto


class CriarCategoriaService:
    @staticmethod
    def executar(dados, id_usuario):
        """id_usuario vem do usuário autenticado (token), nunca do payload
        enviado pelo cliente — cada categoria pertence a quem a criou."""
        nome_categoria = texto(dados.get('nome_categoria'), 'Nome da categoria', 100)
        descricao = texto(dados.get('descricao'), 'Descrição', 255, obrigatorio=False)
        categoria = Categoria(
            nome_categoria=nome_categoria,
            descricao=descricao,
            id_usuario=id_usuario
        )
        categoria.salvar()
        return categoria