from datetime import date

from app.extensions import db


class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id_usuario = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    data_cadastro = db.Column(db.Date, default=date.today)

    assinaturas = db.relationship('Assinatura', backref='usuario', lazy=True)

    def salvar(self):
        db.session.add(self)
        db.session.commit()
        return self

    def atualizar(self, nome=None, email=None, senha_hash=None, role=None):
        if nome is not None:
            self.nome = nome
        if email is not None:
            self.email = email
        if senha_hash is not None:
            self.senha_hash = senha_hash
        if role is not None:
            self.role = role
        db.session.commit()
        return self

    def deletar(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def listar_todos():
        return Usuario.query.all()

    @staticmethod
    def buscar_por_id(id_usuario):
        return db.session.get(Usuario, id_usuario)

    def to_dict(self):
        return {
            'id_usuario': self.id_usuario,
            'nome': self.nome,
            'email': self.email,
            'role': self.role,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None
        }
