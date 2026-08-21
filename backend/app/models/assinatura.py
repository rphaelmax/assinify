from app.extensions import db
from datetime import date


class Assinatura(db.Model):
    __tablename__ = 'assinaturas'

    id_assinatura = db.Column(db.Integer, primary_key=True)
    nome_servico = db.Column(db.String(100), nullable=False)
    valor_mensal = db.Column(db.Float, nullable=False)
    data_renovacao = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='ativa')
    tipo_plano = db.Column(db.String(50), nullable=True)
    metodo_pagamento = db.Column(db.String(30), nullable=False, default='cartao_credito')

    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    id_categoria = db.Column(db.Integer, db.ForeignKey('categorias.id_categoria'), nullable=False)

    def salvar(self):
        db.session.add(self)
        db.session.commit()

    def atualizar(self, nome_servico=None, valor_mensal=None, data_renovacao=None, status=None, tipo_plano=None, metodo_pagamento=None, id_categoria=None):
        if nome_servico is not None:
            self.nome_servico = nome_servico
        if valor_mensal is not None:
            self.valor_mensal = valor_mensal
        if data_renovacao is not None:
            self.data_renovacao = data_renovacao
        if status is not None:
            self.status = status
        if tipo_plano is not None:
            self.tipo_plano = tipo_plano
        if metodo_pagamento is not None:
            self.metodo_pagamento = metodo_pagamento
        if id_categoria is not None:
            self.id_categoria = id_categoria
        db.session.commit()

    def deletar(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def listar_todos():
        return Assinatura.query.all()

    @staticmethod
    def listar_por_usuario(id_usuario):
        return Assinatura.query.filter_by(id_usuario=id_usuario).all()

    @staticmethod
    def buscar_por_id(id):
        return Assinatura.query.get(id)

    def to_dict(self):
        return {
            'id_assinatura': self.id_assinatura,
            'nome_servico': self.nome_servico,
            'valor_mensal': self.valor_mensal,
            'data_renovacao': self.data_renovacao.isoformat() if self.data_renovacao else None,
            'status': self.status,
            'tipo_plano': self.tipo_plano,
            'metodo_pagamento': self.metodo_pagamento,
            'id_usuario': self.id_usuario,
            'id_categoria': self.id_categoria
        }
