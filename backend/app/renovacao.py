"""Cálculo de datas de renovação a partir de data_renovacao + periodicidade.

`data_renovacao` é a data-âncora da assinatura (a primeira cobrança ou a
última informada pelo usuário). As renovações seguintes são derivadas dela:

- mensal: mesmo dia do mês (ajustado para o último dia em meses curtos,
  ex.: âncora dia 31 renova dia 28/29 em fevereiro e volta ao dia 31 depois);
- anual: mesmo dia e mês (29/fev renova em 28/fev em anos não bissextos);
- semanal: a cada 7 dias.
"""
import calendar
from datetime import date, timedelta


def _somar_meses(base, meses):
    indice = base.year * 12 + (base.month - 1) + meses
    ano, mes = divmod(indice, 12)
    mes += 1
    dia = min(base.day, calendar.monthrange(ano, mes)[1])
    return date(ano, mes, dia)


def _somar_anos(base, anos):
    ano = base.year + anos
    dia = min(base.day, calendar.monthrange(ano, base.month)[1])
    return date(ano, base.month, dia)


def proxima_renovacao(data_base, periodicidade, hoje=None):
    """Primeira renovação com data >= hoje (ou a própria âncora, se futura)."""
    hoje = hoje or date.today()
    if data_base >= hoje:
        return data_base

    if periodicidade == 'semanal':
        semanas = -(-(hoje - data_base).days // 7)  # ceil
        return data_base + timedelta(weeks=semanas)

    if periodicidade == 'anual':
        n = hoje.year - data_base.year
        candidata = _somar_anos(data_base, n)
        return candidata if candidata >= hoje else _somar_anos(data_base, n + 1)

    # mensal (padrão)
    n = (hoje.year - data_base.year) * 12 + (hoje.month - data_base.month)
    candidata = _somar_meses(data_base, n)
    return candidata if candidata >= hoje else _somar_meses(data_base, n + 1)


def renovacoes_no_periodo(data_base, periodicidade, inicio, fim):
    """Todas as renovações com inicio <= data <= fim (nunca antes da âncora)."""
    datas = []

    if periodicidade == 'semanal':
        inicio_efetivo = max(inicio, data_base)
        semanas = -(-(inicio_efetivo - data_base).days // 7)
        atual = data_base + timedelta(weeks=semanas)
        while atual <= fim:
            datas.append(atual)
            atual += timedelta(weeks=1)
        return datas

    if periodicidade == 'anual':
        for n in range(max(0, inicio.year - data_base.year), fim.year - data_base.year + 1):
            candidata = _somar_anos(data_base, n)
            if inicio <= candidata <= fim:
                datas.append(candidata)
        return datas

    n_ini = max(0, (inicio.year - data_base.year) * 12 + inicio.month - data_base.month)
    n_fim = (fim.year - data_base.year) * 12 + fim.month - data_base.month
    for n in range(n_ini, n_fim + 1):
        candidata = _somar_meses(data_base, n)
        if inicio <= candidata <= fim:
            datas.append(candidata)
    return datas