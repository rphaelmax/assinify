from app.models.assinatura import Assinatura


class BuscarAssinaturaService:
    @staticmethod
    def executar(id):
        assinatura = Assinatura.buscar_por_id(id)
        if assinatura is None:
            raise ValueError('Assinatura não encontrada')
        return assinatura
