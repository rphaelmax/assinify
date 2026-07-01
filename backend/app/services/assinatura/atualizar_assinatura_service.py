from app.models.assinatura import Assinatura
from datetime import date


class AtualizarAssinaturaService:
    @staticmethod
    def executar(id, dados):
        assinatura = Assinatura.buscar_por_id(id)
        if assinatura is None:
            raise ValueError('Assinatura não encontrada')

        data_renovacao = None
        if dados.get('data_renovacao'):
            data_renovacao = date.fromisoformat(dados['data_renovacao'])

        assinatura.atualizar(
            nome_servico=dados.get('nome_servico'),
            valor_mensal=dados.get('valor_mensal'),
            data_renovacao=data_renovacao,
            status=dados.get('status'),
            tipo_plano=dados.get('tipo_plano'),
            id_categoria=dados.get('id_categoria')
        )
        return assinatura
