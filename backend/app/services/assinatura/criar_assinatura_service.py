from datetime import date

from app.models.assinatura import Assinatura
from app.models.categoria import Categoria
from app.exceptions import ValidationError, NotFoundError, ForbiddenError


METODOS_PAGAMENTO = {
    'cartao_credito', 'cartao_debito', 'pix', 'boleto', 'debito_automatico', 'transferencia', 'outro'
}


class CriarAssinaturaService:
    """Caso de uso: cadastrar uma assinatura para o usuário autenticado."""

    @staticmethod
    def executar(dados, usuario_atual):
        nome_servico = dados.get('nome_servico')
        valor_mensal = dados.get('valor_mensal')
        id_categoria = dados.get('id_categoria')

        if not nome_servico:
            raise ValidationError('Nome do serviço é obrigatório')
        if valor_mensal is None or valor_mensal <= 0:
            raise ValidationError('Valor mensal deve ser maior que zero')
        if not id_categoria:
            raise ValidationError('Categoria é obrigatória')

        categoria = Categoria.buscar_por_id(id_categoria)
        if categoria is None:
            raise NotFoundError('Categoria não encontrada')
        if categoria.id_usuario != usuario_atual.id_usuario:
            raise ForbiddenError('Você só pode usar suas próprias categorias')

        try:
            data_renovacao = (
                date.fromisoformat(dados['data_renovacao'])
                if dados.get('data_renovacao')
                else date.today()
            )
        except ValueError:
            raise ValidationError('Data de renovação inválida')

        metodo_pagamento = dados.get('metodo_pagamento', 'cartao_credito')
        if metodo_pagamento not in METODOS_PAGAMENTO:
            raise ValidationError('Método de pagamento inválido')

        status = dados.get('status', 'ativa')
        if status not in ('ativa', 'cancelada'):
            raise ValidationError("Status inválido. Use 'ativa' ou 'cancelada'")

        assinatura = Assinatura(
            nome_servico=nome_servico,
            valor_mensal=valor_mensal,
            data_renovacao=data_renovacao,
            status=status,
            tipo_plano=dados.get('tipo_plano'),
            metodo_pagamento=metodo_pagamento,
            id_usuario=usuario_atual.id_usuario,
            id_categoria=id_categoria
        )
        assinatura.salvar()
        return assinatura
