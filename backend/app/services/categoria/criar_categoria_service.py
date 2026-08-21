from app.models.categoria import Categoria
from app.exceptions import ValidationError


class CriarCategoriaService:
    @staticmethod
    def executar(dados, id_usuario):
        """id_usuario vem do usuário autenticado (token), nunca do payload
        enviado pelo cliente — cada categoria pertence a quem a criou."""
        if not dados.get('nome_categoria'):
            raise ValidationError('Nome da categoria é obrigatório')
        categoria = Categoria(
            nome_categoria=dados['nome_categoria'],
            descricao=dados.get('descricao'),
            id_usuario=id_usuario
        )
        categoria.salvar()
        return categoria