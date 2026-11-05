from app.armazenamento import ArmazenamentoAvatar
from app.exceptions import ValidationError


class AtualizarFotoService:
    """Troca a foto de perfil do próprio usuário autenticado."""

    @staticmethod
    def executar(arquivo, usuario_atual):
        if arquivo is None or not arquivo.filename:
            raise ValidationError('Envie uma imagem no campo "foto"')

        foto_antiga = usuario_atual.foto_perfil
        foto_nova = ArmazenamentoAvatar.salvar(arquivo, usuario_atual.id_usuario)
        try:
            usuario_atual.definir_foto(foto_nova)
        except Exception:
            ArmazenamentoAvatar.remover(foto_nova)
            raise

        ArmazenamentoAvatar.remover(foto_antiga)
        return usuario_atual
