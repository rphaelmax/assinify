from app.extensions import db
from app.models.usuario import Usuario
from app.models.assinatura import Assinatura
from app.models.historico_assinatura import HistoricoAssinatura
from app.repositories.usuario_repository import UsuarioRepository
from app.exceptions import NotFoundError, ForbiddenError


class DeletarUsuarioService:
    @staticmethod
    def executar(id, usuario_atual):
        usuario = Usuario.buscar_por_id(id)
        if usuario is None:
            raise NotFoundError('Usuário não encontrado')

        if UsuarioRepository.eh_admin_padrao(usuario):
            raise ForbiddenError('O admin padrão não pode ser excluído')

        if usuario.id_usuario == usuario_atual.id_usuario:
            raise ForbiddenError('Você não pode excluir a própria conta')

        # Funciona mesmo em bancos criados sem ON DELETE SET NULL nas FKs do histórico:
        # 1) apaga o histórico das assinaturas do usuário (elas serão excluídas junto);
        # 2) mantém o histórico de alterações que ele fez em assinaturas de outros, sem autor.
        ids_assinaturas = [
            a.id_assinatura for a in Assinatura.query.filter_by(id_usuario=usuario.id_usuario).all()
        ]
        if ids_assinaturas:
            HistoricoAssinatura.query.filter(
                HistoricoAssinatura.id_assinatura.in_(ids_assinaturas)
            ).delete(synchronize_session=False)
        HistoricoAssinatura.query.filter_by(id_usuario=usuario.id_usuario).update(
            {'id_usuario': None}, synchronize_session=False
        )
        db.session.flush()

        usuario.deletar()