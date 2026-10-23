from datetime import datetime

from app.extensions import db


class HistoricoAssinatura(db.Model):
    __tablename__ = 'historico_assinaturas'

    id = db.Column(db.Integer, primary_key=True)
    id_assinatura = db.Column(db.Integer, db.ForeignKey('assinaturas.id_assinatura', ondelete='SET NULL'), nullable=True)
    campo = db.Column(db.String(50), nullable=False)
    valor_antigo = db.Column(db.Text, nullable=True)
    valor_novo = db.Column(db.Text, nullable=True)
    data_alteracao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario', ondelete='SET NULL'), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'id_assinatura': self.id_assinatura,
            'campo': self.campo,
            'valor_antigo': self.valor_antigo,
            'valor_novo': self.valor_novo,
            'data_alteracao': self.data_alteracao.isoformat() if self.data_alteracao else None,
            'id_usuario': self.id_usuario
        }