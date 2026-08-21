from datetime import date

from app.models.assinatura import Assinatura
from app.models.categoria import Categoria
from app.exceptions import NotFoundError, ForbiddenError, ValidationError
from app.services.assinatura.criar_assinatura_service import METODOS_PAGAMENTO


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

        if 'nome_servico' in dados and not dados.get('nome_servico'):
            raise ValidationError('Nome do serviço é obrigatório')

        if 'valor_mensal' in dados:
            if dados['valor_mensal'] is None or dados['valor_mensal'] <= 0:
                raise ValidationError('Valor mensal deve ser maior que zero')

        data_renovacao = None
        if 'data_renovacao' in dados:
            if not dados.get('data_renovacao'):
                raise ValidationError('Data de renovação é obrigatória')
            try:
                data_renovacao = date.fromisoformat(dados['data_renovacao'])
            except ValueError:
                raise ValidationError('Data de renovação inválida')

        if 'metodo_pagamento' in dados and dados['metodo_pagamento'] not in METODOS_PAGAMENTO:
            raise ValidationError('Método de pagamento inválido')

        if 'status' in dados and dados['status'] not in ('ativa', 'cancelada'):
            raise ValidationError("Status inválido. Use 'ativa' ou 'cancelada'")

        if 'id_categoria' in dados:
            if not dados.get('id_categoria'):
                raise ValidationError('Categoria é obrigatória')
            categoria = Categoria.buscar_por_id(dados['id_categoria'])
            if categoria is None:
                raise NotFoundError('Categoria não encontrada')
            if (
                usuario_atual.role != 'admin'
                and categoria.id_usuario != usuario_atual.id_usuario
            ):
                raise ForbiddenError('Você só pode usar suas próprias categorias')

        assinatura.atualizar(
            nome_servico=dados.get('nome_servico'),
            valor_mensal=dados.get('valor_mensal'),
            data_renovacao=data_renovacao,
            status=dados.get('status'),
            tipo_plano=dados.get('tipo_plano'),
            metodo_pagamento=dados.get('metodo_pagamento'),
            id_categoria=dados.get('id_categoria')
        )
        return assinatura
