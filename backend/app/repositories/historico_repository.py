from sqlalchemy import desc

from app.extensions import db
from app.models.assinatura import Assinatura
from app.models.historico_assinatura import HistoricoAssinatura


class HistoricoRepository:
    """Persistência e consultas do histórico de alterações das assinaturas."""

    @staticmethod
    def listar_por_assinatura(id_assinatura):
        return (
            HistoricoAssinatura.query
            .filter_by(id_assinatura=id_assinatura)
            .order_by(HistoricoAssinatura.data_alteracao.desc(), HistoricoAssinatura.id.desc())
            .all()
        )

    @staticmethod
    def listar_alteracoes_valor(id_usuario, limite=100):
        """Alterações de valor das assinaturas do usuário (mais recentes primeiro).

        Devolve tuplas (HistoricoAssinatura, nome_servico). Assinaturas já
        excluídas ficam de fora porque o vínculo vira NULL.
        """
        return (
            db.session.query(HistoricoAssinatura, Assinatura.nome_servico)
            .join(Assinatura, Assinatura.id_assinatura == HistoricoAssinatura.id_assinatura)
            .filter(
                Assinatura.id_usuario == id_usuario,
                HistoricoAssinatura.campo == 'valor_mensal',
            )
            .order_by(desc(HistoricoAssinatura.data_alteracao), desc(HistoricoAssinatura.id))
            .limit(limite)
            .all()
        )

    @staticmethod
    def registrar_alteracoes(id_assinatura, id_usuario, alteracoes):
        """Grava uma linha por campo alterado.

        `alteracoes` é uma lista de tuplas (campo, valor_antigo, valor_novo).
        Em caso de falha desfaz a transação e relança a exceção.
        """
        try:
            for campo, valor_antigo, valor_novo in alteracoes:
                db.session.add(HistoricoAssinatura(
                    id_assinatura=id_assinatura,
                    campo=campo,
                    valor_antigo=valor_antigo,
                    valor_novo=valor_novo,
                    id_usuario=id_usuario
                ))
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def desvincular_usuario(id_usuario):
        """Prepara a exclusão de um usuário sem depender de ON DELETE SET NULL no banco:
        1) apaga o histórico das assinaturas dele (que serão excluídas junto);
        2) mantém, sem autor, o histórico das alterações que ele fez em assinaturas de outros.
        """
        ids_assinaturas = [
            a.id_assinatura for a in Assinatura.query.filter_by(id_usuario=id_usuario).all()
        ]
        if ids_assinaturas:
            HistoricoAssinatura.query.filter(
                HistoricoAssinatura.id_assinatura.in_(ids_assinaturas)
            ).delete(synchronize_session=False)
        HistoricoAssinatura.query.filter_by(id_usuario=id_usuario).update(
            {'id_usuario': None}, synchronize_session=False
        )
        db.session.flush()