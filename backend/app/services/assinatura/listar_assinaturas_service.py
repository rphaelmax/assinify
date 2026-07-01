from app.models.assinatura import Assinatura


class ListarAssinaturasService:
    @staticmethod
    def executar():
        return Assinatura.listar_todos()
