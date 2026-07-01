from app.models.assinatura import Assinatura
from datetime import date


class CriarAssinaturaService:
    @staticmethod
    def executar(dados):
        if not dados.get('nome_servico'):
            raise ValueError('Nome do serviço é obrigatório')
        if not dados.get('valor_mensal'):
            raise ValueError('Valor mensal é obrigatório')
        if not dados.get('id_usuario'):
            raise ValueError('Usuário é obrigatório')
        if not dados.get('id_categoria'):
            raise ValueError('Categoria é obrigatória')

        assinatura = Assinatura(
            nome_servico=dados['nome_servico'],
            valor_mensal=dados['valor_mensal'],
            data_renovacao=date.fromisoformat(dados['data_renovacao']) if dados.get('data_renovacao') else date.today(),
            status=dados.get('status', 'ativa'),
            tipo_plano=dados.get('tipo_plano'),
            id_usuario=dados['id_usuario'],
            id_categoria=dados['id_categoria']
        )
        assinatura.salvar()
        return assinatura
