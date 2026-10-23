from app.models.assinatura import Assinatura
from app.models.categoria import Categoria
from app.exceptions import NotFoundError, ForbiddenError, ValidationError
from app.services.assinatura.criar_assinatura_service import METODOS_PAGAMENTO
from app.validacao import texto, valor_monetario, data_iso, exigir_id_categoria, validar_periodicidade


CAMPOS_HISTORICO = ('nome_servico', 'valor_mensal', 'periodicidade', 'data_renovacao', 'status', 'tipo_plano', 'metodo_pagamento', 'id_categoria')


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

        nome_servico = texto(dados['nome_servico'], 'Nome do serviço', 100) if 'nome_servico' in dados else None
        valor_mensal = valor_monetario(dados['valor_mensal']) if 'valor_mensal' in dados else None
        data_renovacao = data_iso(dados['data_renovacao'], 'Data de renovação') if 'data_renovacao' in dados else None
        tipo_plano = texto(dados['tipo_plano'], 'Tipo de plano', 50, obrigatorio=False) if 'tipo_plano' in dados else None

        if 'metodo_pagamento' in dados and (
            not isinstance(dados['metodo_pagamento'], str)
            or dados['metodo_pagamento'] not in METODOS_PAGAMENTO
        ):
            raise ValidationError('Método de pagamento inválido')

        if 'periodicidade' in dados:
            validar_periodicidade(dados['periodicidade'])

        if 'status' in dados and dados['status'] not in ('ativa', 'cancelada'):
            raise ValidationError("Status inválido. Use 'ativa' ou 'cancelada'")

        id_categoria = None
        if 'id_categoria' in dados:
            id_categoria = exigir_id_categoria(dados['id_categoria'])
            categoria = Categoria.buscar_por_id(id_categoria)
            if categoria is None:
                raise NotFoundError('Categoria não encontrada')
            if categoria.id_usuario != assinatura.id_usuario:
                raise ForbiddenError('A categoria deve pertencer ao dono da assinatura')

        assinatura.atualizar(
            nome_servico=nome_servico,
            valor_mensal=valor_mensal,
            data_renovacao=data_renovacao,
            status=dados.get('status'),
            tipo_plano=tipo_plano,
            metodo_pagamento=dados.get('metodo_pagamento'),
            periodicidade=dados.get('periodicidade'),
            id_categoria=id_categoria
        )

        # Histórico: diff silencioso — não falha a atualização se o log falhar
        try:
            from app.models.historico_assinatura import HistoricoAssinatura
            from app.extensions import db
            novo = assinatura.to_dict()
            for campo in CAMPOS_HISTORICO:
                antigo_v = snapshot.get(campo)
                novo_v = novo.get(campo)
                # Normaliza para comparação textual
                if str(antigo_v) != str(novo_v):
                    # Só registra se o campo foi enviado na requisição
                    if campo in dados:
                        db.session.add(HistoricoAssinatura(
                            id_assinatura=assinatura.id_assinatura,
                            campo=campo,
                            valor_antigo=str(antigo_v) if antigo_v is not None else None,
                            valor_novo=str(novo_v) if novo_v is not None else None,
                            id_usuario=usuario_atual.id_usuario
                        ))
            db.session.commit()
        except Exception:
            from app.extensions import db as _db
            try:
                _db.session.rollback()
            except Exception:
                pass
            # Log silencioso — evita quebrar a atualização
            import logging
            logging.getLogger(__name__).exception('Falha ao gravar historico_assinaturas')

        return assinatura
