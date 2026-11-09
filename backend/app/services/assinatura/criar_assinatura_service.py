from datetime import date

from app.models.assinatura import Assinatura
from app.models.categoria import Categoria
from app.exceptions import ValidationError, NotFoundError, ForbiddenError
from app.validacao import (
    texto, valor_monetario, data_iso, data_iso_opcional, exigir_id_categoria, validar_periodicidade,
    validar_moeda, validar_num_pessoas, validar_status, resolver_data_cancelamento,
    alinhar_renovacao_ao_teste
)


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

        moeda = validar_moeda(dados.get('moeda'), padrao=usuario_atual.moeda_base or 'BRL')
        num_pessoas = validar_num_pessoas(dados.get('num_pessoas'))
        teste_ate = data_iso_opcional(dados.get('teste_ate'), 'Fim do teste')

        status = validar_status(dados.get('status', 'ativa'))
        data_cancelamento = resolver_data_cancelamento(
            status, data_iso_opcional(dados.get('data_cancelamento'), 'Data de cancelamento')
        )
        if status == 'ativa':
            data_renovacao = alinhar_renovacao_ao_teste(data_renovacao, teste_ate)

        assinatura = Assinatura(
            nome_servico=nome_servico,
            valor_mensal=valor_mensal,
            moeda=moeda,
            num_pessoas=num_pessoas,
            data_renovacao=data_renovacao,
            status=status,
            data_cancelamento=data_cancelamento,
            teste_ate=teste_ate,
            tipo_plano=tipo_plano,
            metodo_pagamento=metodo_pagamento,
            periodicidade=periodicidade,
            id_usuario=usuario_atual.id_usuario,
            id_categoria=id_categoria
        )
        assinatura.salvar()
        return assinatura
