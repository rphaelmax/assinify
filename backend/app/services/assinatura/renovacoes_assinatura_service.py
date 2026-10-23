from datetime import date
import calendar

from app.models.assinatura import Assinatura
from app.exceptions import ValidationError
from app.renovacao import renovacoes_no_periodo

LIMITE_PROXIMAS_PADRAO = 50
LIMITE_PROXIMAS_MAXIMO = 200


def _inteiro(valor, campo, minimo, maximo):
    try:
        numero = int(valor)
    except (TypeError, ValueError):
        raise ValidationError(f'{campo} inválido')
    if not minimo <= numero <= maximo:
        raise ValidationError(f'{campo} inválido')
    return numero


class RenovacoesAssinaturaService:
    """Agenda de renovações das assinaturas ativas do usuário.

    Independe da paginação da listagem: o dashboard usa isto para
    "próximas renovações", notificações e calendário.
    """

    @staticmethod
    def proximas(usuario_atual, limite=None):
        limite = (
            LIMITE_PROXIMAS_PADRAO
            if limite in (None, '')
            else _inteiro(limite, 'Limite', 1, LIMITE_PROXIMAS_MAXIMO)
        )
        ativas = Assinatura.query.filter_by(
            id_usuario=usuario_atual.id_usuario, status='ativa'
        ).all()
        ativas = [a for a in ativas if a.proxima_renovacao is not None]
        ativas.sort(key=lambda a: (a.proxima_renovacao, a.nome_servico.lower()))
        return ativas[:limite]

    @staticmethod
    def calendario(usuario_atual, ano=None, mes=None):
        hoje = date.today()
        ano = hoje.year if ano in (None, '') else _inteiro(ano, 'Ano', 1970, 2100)
        mes = hoje.month if mes in (None, '') else _inteiro(mes, 'Mês', 1, 12)

        inicio = date(ano, mes, 1)
        fim = date(ano, mes, calendar.monthrange(ano, mes)[1])

        ativas = Assinatura.query.filter_by(
            id_usuario=usuario_atual.id_usuario, status='ativa'
        ).all()

        renovacoes = []
        for a in ativas:
            for data in renovacoes_no_periodo(
                a.data_renovacao, a.periodicidade or 'mensal', inicio, fim
            ):
                renovacoes.append({
                    'dia': data.day,
                    'id_assinatura': a.id_assinatura,
                    'nome_servico': a.nome_servico,
                    'valor_mensal': float(a.valor_mensal),
                    'periodicidade': a.periodicidade or 'mensal',
                })
        renovacoes.sort(key=lambda r: (r['dia'], r['nome_servico'].lower()))
        return {'ano': ano, 'mes': mes, 'renovacoes': renovacoes}