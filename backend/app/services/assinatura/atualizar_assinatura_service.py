import logging
from app.models.assinatura import Assinatura
from app.models.categoria import Categoria
from app.repositories.historico_repository import HistoricoRepository
from app.exceptions import NotFoundError, ForbiddenError, ValidationError
from app.services.assinatura.criar_assinatura_service import METODOS_PAGAMENTO
from app.validacao import (
    texto, valor_monetario, data_iso, data_iso_opcional, exigir_id_categoria, validar_periodicidade,
    validar_moeda, validar_num_pessoas, validar_status, resolver_data_cancelamento,
    alinhar_renovacao_ao_teste
)

logger = logging.getLogger(__name__)

CAMPOS_HISTORICO = (
    'nome_servico', 'valor_mensal', 'moeda', 'num_pessoas', 'periodicidade', 'data_renovacao',
    'status', 'data_cancelamento', 'teste_ate', 'tipo_plano', 'metodo_pagamento', 'id_categoria'
)
# Campos que mudam como consequência de outro (ex.: cancelar define a data): sempre comparados.
CAMPOS_DERIVADOS = ('data_cancelamento',)


class AtualizarAssinaturaService:
    """Caso de uso: atualizar uma assinatura acessível ao usuário."""

    @staticmethod
    def executar(id, dados, usuario_atual):
        assinatura = Assinatura.buscar_por_id(id)
        if assinatura is None:
            raise NotFoundError('Assinatura não encontrada')

        if (
            usuario_atual.role != 'admin'
            and assinatura.id_usuario != usuario_atual.id_usuario
        ):
            raise ForbiddenError('Você só pode alterar suas próprias assinaturas')

        snapshot = assinatura.to_dict()

        # Só entram em `campos` as chaves enviadas; None é um valor válido (ex.: limpar teste_ate).
        campos = {}
        if 'nome_servico' in dados:
            campos['nome_servico'] = texto(dados['nome_servico'], 'Nome do serviço', 100)
        if 'valor_mensal' in dados:
            campos['valor_mensal'] = valor_monetario(dados['valor_mensal'])
        if 'moeda' in dados:
            campos['moeda'] = validar_moeda(dados['moeda'], padrao=assinatura.moeda)
        if 'num_pessoas' in dados:
            campos['num_pessoas'] = validar_num_pessoas(dados['num_pessoas'])
        if 'data_renovacao' in dados:
            campos['data_renovacao'] = data_iso(dados['data_renovacao'], 'Data de renovação')
        if 'tipo_plano' in dados:
            campos['tipo_plano'] = texto(dados['tipo_plano'], 'Tipo de plano', 50, obrigatorio=False)
        if 'teste_ate' in dados:
            campos['teste_ate'] = data_iso_opcional(dados['teste_ate'], 'Fim do teste')

        if 'metodo_pagamento' in dados:
            if (
                not isinstance(dados['metodo_pagamento'], str)
                or dados['metodo_pagamento'] not in METODOS_PAGAMENTO
            ):
                raise ValidationError('Método de pagamento inválido')
            campos['metodo_pagamento'] = dados['metodo_pagamento']

        if 'periodicidade' in dados:
            campos['periodicidade'] = validar_periodicidade(dados['periodicidade'])

        if 'id_categoria' in dados:
            id_categoria = exigir_id_categoria(dados['id_categoria'])
            categoria = Categoria.buscar_por_id(id_categoria)
            if categoria is None:
                raise NotFoundError('Categoria não encontrada')
            if categoria.id_usuario != assinatura.id_usuario:
                raise ForbiddenError('A categoria deve pertencer ao dono da assinatura')
            campos['id_categoria'] = id_categoria

        # Status e data de cancelamento andam juntos
        if 'status' in dados or 'data_cancelamento' in dados:
            status = validar_status(dados['status']) if 'status' in dados else assinatura.status
            informada = (
                data_iso_opcional(dados['data_cancelamento'], 'Data de cancelamento')
                if 'data_cancelamento' in dados else None
            )
            campos['status'] = status
            campos['data_cancelamento'] = resolver_data_cancelamento(
                status, informada, atual=assinatura.data_cancelamento
            )

        # Primeira cobrança só depois do teste gratuito (vale só para assinatura ativa)
        if campos.get('status', assinatura.status) == 'ativa':
            teste_ate = campos['teste_ate'] if 'teste_ate' in campos else assinatura.teste_ate
            renovacao = campos.get('data_renovacao', assinatura.data_renovacao)
            alinhada = alinhar_renovacao_ao_teste(renovacao, teste_ate)
            if alinhada != renovacao:
                campos['data_renovacao'] = alinhada

        assinatura.atualizar(**campos)

        # Histórico: registra só os campos que realmente mudaram.
        # Falha no log não deve quebrar a atualização.
        novo = assinatura.to_dict()
        alteracoes = [
            (
                campo,
                None if snapshot.get(campo) is None else str(snapshot[campo]),
                None if novo.get(campo) is None else str(novo[campo])
            )
            for campo in CAMPOS_HISTORICO
            if (campo in dados or campo in CAMPOS_DERIVADOS)
            and str(snapshot.get(campo)) != str(novo.get(campo))
        ]
        if alteracoes:
            try:
                HistoricoRepository.registrar_alteracoes(
                    assinatura.id_assinatura, usuario_atual.id_usuario, alteracoes
                )
            except Exception:
                logger.exception('Falha ao gravar historico_assinaturas')

        return assinatura
