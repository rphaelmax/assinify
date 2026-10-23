from datetime import date

from app.models.assinatura import Assinatura
from app.models.categoria import Categoria
from app.exceptions import ValidationError, NotFoundError, ForbiddenError
from app.validacao import texto, valor_monetario, data_iso, exigir_id_categoria, validar_periodicidade


METODOS_PAGAMENTO = {
    'cartao_credito', 'cartao_debito', 'pix', 'boleto', 'debito_automatico', 'transferencia', 'outro'
}


class CriarAssinaturaService:
    """Caso de uso: cadastrar uma assinatura para o usuário autenticado."""

    @staticmethod
    def executar(dados, usuario_atual):
        nome_servico = texto(dados.get('nome_servico'), 'Nome do serviço', 100)
        valor_mensal = valor_monetario(dados.get('valor_mensal'))
        id_categoria = exigir_id_categoria(dados.get('id_categoria'))
        tipo_plano = texto(dados.get('tipo_plano'), 'Tipo de plano', 50, obrigatorio=False)

        categoria = Categoria.buscar_por_id(id_categoria)
        if categoria is None:
            raise NotFoundError('Categoria não encontrada')
        if categoria.id_usuario != usuario_atual.id_usuario:
            raise ForbiddenError('Você só pode usar suas próprias categorias')

        data_renovacao = (
            data_iso(dados['data_renovacao'], 'Data de renovação')
            if dados.get('data_renovacao')
            else date.today()
        )

        metodo_pagamento = dados.get('metodo_pagamento', 'cartao_credito')
        if not isinstance(metodo_pagamento, str) or metodo_pagamento not in METODOS_PAGAMENTO:
            raise ValidationError('Método de pagamento inválido')

        periodicidade = validar_periodicidade(dados.get('periodicidade'))

        status = dados.get('status', 'ativa')
        if status not in ('ativa', 'cancelada'):
            raise ValidationError("Status inválido. Use 'ativa' ou 'cancelada'")

        assinatura = Assinatura(
            nome_servico=nome_servico,
            valor_mensal=valor_mensal,
            data_renovacao=data_renovacao,
            status=status,
            tipo_plano=tipo_plano,
            metodo_pagamento=metodo_pagamento,
            periodicidade=periodicidade,
            id_usuario=usuario_atual.id_usuario,
            id_categoria=id_categoria
        )
        assinatura.salvar()
        return assinatura
