from datetime import date
from decimal import Decimal

from app.cambio import fator as fator_cambio
from app.extensions import db
from app.moedas import MOEDA_PADRAO
from app.renovacao import (
    proxima_renovacao as calcular_proxima_renovacao,
    renovacoes_no_periodo as calcular_renovacoes_no_periodo,
)

PERIODICIDADES = {'semanal', 'mensal', 'anual'}
FATOR_ANUAL = {'semanal': Decimal('52'), 'mensal': Decimal('12'), 'anual': Decimal('1')}
STATUS_VALIDOS = ('ativa', 'pausada', 'cancelada')

CAMPOS_ATUALIZAVEIS = {
    'nome_servico', 'valor_mensal', 'moeda', 'num_pessoas', 'data_renovacao', 'status',
    'data_cancelamento', 'teste_ate', 'tipo_plano', 'metodo_pagamento', 'periodicidade',
    'id_categoria',
}


def _dinheiro(valor):
    return round(float(valor), 2)


class Assinatura(db.Model):
    __tablename__ = 'assinaturas'

    id_assinatura = db.Column(db.Integer, primary_key=True)
    nome_servico = db.Column(db.String(100), nullable=False)
    # Preço cheio cobrado por período, na moeda da assinatura (o nome é histórico).
    valor_mensal = db.Column(db.Numeric(10, 2), nullable=False)
    moeda = db.Column(db.String(3), nullable=False, default=MOEDA_PADRAO)
    # Quantas pessoas dividem a assinatura, contando com o dono (1 = só ele paga).
    num_pessoas = db.Column(db.Integer, nullable=False, default=1)
    data_renovacao = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='ativa')
    data_cancelamento = db.Column(db.Date, nullable=True)
    # Último dia do teste gratuito: a primeira cobrança acontece a partir dele.
    teste_ate = db.Column(db.Date, nullable=True)
    tipo_plano = db.Column(db.String(50), nullable=True)
    metodo_pagamento = db.Column(db.String(30), nullable=False, default='cartao_credito')
    periodicidade = db.Column(db.String(20), nullable=False, default='mensal')

    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    id_categoria = db.Column(db.Integer, db.ForeignKey('categorias.id_categoria'), nullable=False)

    # ---------- valores ----------

    @property
    def _preco(self):
        return self.valor_mensal if isinstance(self.valor_mensal, Decimal) else Decimal(str(self.valor_mensal))

    @property
    def pessoas(self):
        return self.num_pessoas or 1

    @property
    def valor_minha_parte(self):
        """Parte do dono por período, na moeda da assinatura."""
        return self._preco / self.pessoas

    @property
    def valor_anualizado(self):
        """Parte do dono por ano, na moeda da assinatura."""
        fator = FATOR_ANUAL.get(self.periodicidade or 'mensal', Decimal('12'))
        return self.valor_minha_parte * fator

    @property
    def moeda_base(self):
        """Moeda base do dono da assinatura (para onde os valores são convertidos)."""
        dono = self.usuario
        return (dono.moeda_base if dono is not None and dono.moeda_base else MOEDA_PADRAO)

    def minha_parte_em(self, moeda_base):
        return self.valor_minha_parte * fator_cambio(self.moeda or MOEDA_PADRAO, moeda_base)

    def anualizado_em(self, moeda_base):
        return self.valor_anualizado * fator_cambio(self.moeda or MOEDA_PADRAO, moeda_base)

    # ---------- teste gratuito e renovações ----------

    def em_teste(self, hoje=None):
        hoje = hoje or date.today()
        return self.status == 'ativa' and self.teste_ate is not None and self.teste_ate > hoje

    @property
    def proxima_renovacao(self):
        """Próxima data de cobrança (None se pausada, cancelada ou sem data-âncora).

        Durante o teste gratuito não há cobrança: a próxima é a primeira
        renovação em ou depois do fim do teste.
        """
        if self.status != 'ativa' or not self.data_renovacao:
            return None
        referencia = self.teste_ate if self.em_teste() else None
        return calcular_proxima_renovacao(
            self.data_renovacao, self.periodicidade or 'mensal', hoje=referencia
        )

    def renovacoes_no_periodo(self, inicio, fim):
        """Cobranças entre duas datas, ignorando renovações dentro do teste gratuito."""
        datas = calcular_renovacoes_no_periodo(
            self.data_renovacao, self.periodicidade or 'mensal', inicio, fim
        )
        if self.teste_ate is not None:
            datas = [d for d in datas if d >= self.teste_ate]
        return datas

    # ---------- persistência ----------

    def salvar(self):
        db.session.add(self)
        db.session.commit()

    def atualizar(self, **campos):
        """Aplica só os campos informados (None é um valor válido, ex.: limpar teste_ate)."""
        for nome, valor in campos.items():
            if nome not in CAMPOS_ATUALIZAVEIS:
                raise ValueError(f'Campo não atualizável: {nome}')
            setattr(self, nome, valor)
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
        hoje = date.today()
        proxima = self.proxima_renovacao
        base = self.moeda_base
        em_teste = self.em_teste(hoje)
        return {
            'id_assinatura': self.id_assinatura,
            'nome_servico': self.nome_servico,
            # preço cheio por período, na moeda da assinatura
            'valor_mensal': float(self.valor_mensal),
            'moeda': self.moeda or MOEDA_PADRAO,
            'num_pessoas': self.pessoas,
            # parte do dono por período, na moeda da assinatura
            'valor_minha_parte': _dinheiro(self.valor_minha_parte),
            # parte do dono por ano, já convertida para a moeda base
            'valor_anualizado': _dinheiro(self.anualizado_em(base)),
            'moeda_base': base,
            'periodicidade': self.periodicidade,
            'data_renovacao': self.data_renovacao.isoformat() if self.data_renovacao else None,
            'proxima_renovacao': proxima.isoformat() if proxima else None,
            'status': self.status,
            'data_cancelamento': self.data_cancelamento.isoformat() if self.data_cancelamento else None,
            'teste_ate': self.teste_ate.isoformat() if self.teste_ate else None,
            'em_teste': em_teste,
            'dias_teste_restantes': (self.teste_ate - hoje).days if em_teste else None,
            'tipo_plano': self.tipo_plano,
            'metodo_pagamento': self.metodo_pagamento,
            'id_usuario': self.id_usuario,
            'id_categoria': self.id_categoria
        }
