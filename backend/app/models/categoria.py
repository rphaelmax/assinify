from app.extensions import db


class Categoria(db.Model):
    __tablename__ = 'categorias'

    id_categoria = db.Column(db.Integer, primary_key=True)
    nome_categoria = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(255), nullable=True)

    assinaturas = db.relationship('Assinatura', backref='categoria', lazy=True)

    def salvar(self):
        db.session.add(self)
        db.session.commit()

    def atualizar(self, nome_categoria=None, descricao=None):
        if nome_categoria is not None:
            self.nome_categoria = nome_categoria
        if descricao is not None:
            self.descricao = descricao
        db.session.commit()

    def deletar(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def listar_todos():
        return Categoria.query.all()

    @staticmethod
    def buscar_por_id(id):
        return Categoria.query.get(id)

    def to_dict(self):
        return {
            'id_categoria': self.id_categoria,
            'nome_categoria': self.nome_categoria,
            'descricao': self.descricao
        }
