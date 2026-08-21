from app.models.assinatura import Assinatura


class ListarAssinaturasService:
    """Caso de uso: listar assinaturas conforme o perfil autenticado."""

    @staticmethod
    def executar(usuario_atual):
        if usuario_atual.role == 'admin':
            return Assinatura.listar_todos()
        return Assinatura.listar_por_usuario(usuario_atual.id_usuario)
