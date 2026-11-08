from datetime import datetime

from app.extensions import db


class TaxaCambio(db.Model):
    """Última cotação conhecida de cada moeda, em unidades da moeda por 1 USD.

    Serve de reserva quando a API de câmbio está fora do ar e evita buscar
    cotações a cada reinício do servidor.
    """
    __tablename__ = 'taxas_cambio'

    moeda = db.Column(db.String(3), primary_key=True)
    taxa_por_usd = db.Column(db.Numeric(20, 8), nullable=False)
    atualizada_em = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
