from app.armazenamento import ArmazenamentoAvatar


class RemoverFotoService:
    """Remove a foto de perfil do usuário autenticado (volta a mostrar a inicial)."""

    @staticmethod
    def executar(usuario_atual):
        foto = usuario_atual.foto_perfil
        if foto:
            usuario_atual.definir_foto(None)
            ArmazenamentoAvatar.remover(foto)
        return usuario_atual
