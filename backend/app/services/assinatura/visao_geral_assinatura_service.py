import calendar
import statistics
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation

from app.cambio import info as info_cambio
from app.models.assinatura import Assinatura
from app.models.categoria import Categoria
from app.moedas import MOEDA_PADRAO
from app.repositories.historico_repository import HistoricoRepository

MESES_PROJECAO = 12
JANELAS_COBRANCA = (7, 30, 90)
MAX_MAIORES = 8
MAX_REAJUSTES = 5

# (rótulo, mínimo inclusive, máximo exclusivo) em R$ sobre o valor mensal equivalente
FAIXAS_VALOR = (
    ('Até 10', 0, 10),
    ('10 a 25', 10, 25),
    ('25 a 50', 25, 50),
    ('50 a 100', 50, 100),
    ('100+', 100, None),
)

ORDEM_PERIODICIDADE = ('semanal', 'mensal', 'anual')


def _dinheiro(valor):
    return round(float(valor), 2)


def _percentual(parte, total):
    return round(parte / total * 100, 1) if total else 0.0


def _decimal(texto):
    try:
        return Decimal(str(texto))
    except (InvalidOperation, TypeError, ValueError):
        return None


def _item(assinatura, categorias, moeda_base):
    """Resumo de uma assinatura: parte do usuário, convertida para a moeda base."""
    anual = float(assinatura.anualizado_em(moeda_base))
    return {
        'id_assinatura': assinatura.id_assinatura,
        'nome_servico': assinatura.nome_servico,
        'categoria': categorias.get(assinatura.id_categoria, 'Sem categoria'),
        'periodicidade': assinatura.periodicidade or 'mensal',
        'metodo_pagamento': assinatura.metodo_pagamento,
        'valor_periodo': float(assinatura.minha_parte_em(moeda_base)),
        'anual': anual,
        'mensal': anual / 12,
        'data_cancelamento': assinatura.data_cancelamento,
        'teste_ate': assinatura.teste_ate,
    }


def _economizado(item, hoje):
    """Quanto o usuário já deixou de pagar desde a data de cancelamento (0 se não houver data)."""
    cancelada_em = item['data_cancelamento']
    if not cancelada_em:
        return 0.0
    return item['anual'] / 365 * max(0, (hoje - cancelada_em).days)


def _agrupar(itens, chave):
    grupos = {}
    for item in itens:
        grupo = grupos.setdefault(item[chave], {'qtd': 0, 'anual': 0.0})
        grupo['qtd'] += 1
        grupo['anual'] += item['anual']
    return grupos


def _somar_meses(ano, mes, meses):
    indice = ano * 12 + (mes - 1) + meses
    novo_ano, novo_mes = divmod(indice, 12)
    return novo_ano, novo_mes + 1


class VisaoGeralAssinaturaService:
    """Estatísticas elaboradas para a aba Estatísticas.

    Complementa EstatisticasAssinaturaService (cards e gráficos do dashboard):
    aqui entram projeção de caixa, concentração, perfil das assinaturas,
    canceladas e reajustes de preço. Tudo normalizado por valor anualizado.
    """

    @staticmethod
    def executar(usuario_atual):
        id_usuario = usuario_atual.id_usuario
        moeda_base = usuario_atual.moeda_base or MOEDA_PADRAO
        hoje = date.today()

        categorias = {
            c.id_categoria: c.nome_categoria
            for c in Categoria.listar_por_usuario(id_usuario)
        }
        assinaturas = Assinatura.listar_por_usuario(id_usuario)
        # `ativas` inclui as em teste; os totais de gasto usam só quem já cobra.
        ativas = [a for a in assinaturas if a.status == 'ativa']
        em_teste = [a for a in ativas if a.em_teste(hoje)]
        cobrando = [a for a in ativas if not a.em_teste(hoje)]
        pausadas = [a for a in assinaturas if a.status == 'pausada']
        canceladas = [a for a in assinaturas if a.status == 'cancelada']

        itens = [_item(a, categorias, moeda_base) for a in cobrando]
        itens_cancelados = [_item(a, categorias, moeda_base) for a in canceladas]
        itens_pausados = [_item(a, categorias, moeda_base) for a in pausadas]
        itens_teste = [_item(a, categorias, moeda_base) for a in em_teste]

        total_anual = sum(i['anual'] for i in itens)
        total_mensal = total_anual / 12
        mensais = [i['mensal'] for i in itens]

        por_valor = sorted(itens, key=lambda i: i['anual'], reverse=True)
        maiores = [
            {
                'id_assinatura': i['id_assinatura'],
                'nome_servico': i['nome_servico'],
                'categoria': i['categoria'],
                'periodicidade': i['periodicidade'],
                'valor_periodo': _dinheiro(i['valor_periodo']),
                'total_mensal': _dinheiro(i['mensal']),
                'total_anual': _dinheiro(i['anual']),
                'percentual': _percentual(i['anual'], total_anual),
            }
            for i in por_valor[:MAX_MAIORES]
        ]

        economia_anual = sum(i['anual'] for i in itens_cancelados)
        economia_acumulada = sum(_economizado(i, hoje) for i in itens_cancelados)
        total = len(ativas) + len(canceladas)

        resumo = {
            'total_mensal': _dinheiro(total_mensal),
            'total_anual': _dinheiro(total_anual),
            'custo_diario': _dinheiro(total_anual / 365),
            'ativas': len(ativas),
            'em_teste': len(em_teste),
            'pausadas': len(pausadas),
            'canceladas': len(canceladas),
            'total': total,
            'taxa_cancelamento': _percentual(len(canceladas), total),
            'media_mensal': _dinheiro(statistics.mean(mensais)) if mensais else 0.0,
            'mediana_mensal': _dinheiro(statistics.median(mensais)) if mensais else 0.0,
            'maior': maiores[0] if maiores else None,
            'menor': (
                {
                    'nome_servico': por_valor[-1]['nome_servico'],
                    'total_mensal': _dinheiro(por_valor[-1]['mensal']),
                }
                if por_valor else None
            ),
            'concentracao_top3': _percentual(
                sum(i['anual'] for i in por_valor[:3]), total_anual
            ),
            'economia_mensal': _dinheiro(economia_anual / 12),
            'economia_anual': _dinheiro(economia_anual),
            'economia_acumulada': _dinheiro(economia_acumulada),
        }

        return {
            'moeda_base': moeda_base,
            'cambio': info_cambio(),
            'resumo': resumo,
            'maiores': maiores,
            'por_categoria': VisaoGeralAssinaturaService._por_categoria(itens, total_anual),
            'por_periodicidade': VisaoGeralAssinaturaService._por_periodicidade(itens, total_anual),
            'por_pagamento': VisaoGeralAssinaturaService._por_pagamento(itens, total_anual),
            'faixas_valor': VisaoGeralAssinaturaService._faixas(itens),
            'projecao': VisaoGeralAssinaturaService._projecao(ativas, hoje, moeda_base),
            'proximas_cobrancas': VisaoGeralAssinaturaService._proximas_cobrancas(ativas, hoje, moeda_base),
            'canceladas': [
                {
                    'nome_servico': i['nome_servico'],
                    'periodicidade': i['periodicidade'],
                    'total_mensal': _dinheiro(i['mensal']),
                    'total_anual': _dinheiro(i['anual']),
                    'data_cancelamento': i['data_cancelamento'].isoformat() if i['data_cancelamento'] else None,
                    'economizado': _dinheiro(_economizado(i, hoje)),
                }
                for i in sorted(itens_cancelados, key=lambda i: i['anual'], reverse=True)
            ],
            'pausadas': [
                {
                    'nome_servico': i['nome_servico'],
                    'periodicidade': i['periodicidade'],
                    'total_mensal': _dinheiro(i['mensal']),
                    'total_anual': _dinheiro(i['anual']),
                }
                for i in sorted(itens_pausados, key=lambda i: i['anual'], reverse=True)
            ],
            'em_teste': [
                {
                    'nome_servico': i['nome_servico'],
                    'periodicidade': i['periodicidade'],
                    'teste_ate': i['teste_ate'].isoformat(),
                    'dias_restantes': (i['teste_ate'] - hoje).days,
                    'total_mensal': _dinheiro(i['mensal']),
                    'total_anual': _dinheiro(i['anual']),
                }
                for i in sorted(itens_teste, key=lambda i: i['teste_ate'])
            ],
            'reajustes': VisaoGeralAssinaturaService._reajustes(id_usuario),
        }

    # ---------- blocos ----------

    @staticmethod
    def _por_categoria(itens, total_anual):
        grupos = _agrupar(itens, 'categoria')
        return [
            {
                'nome_categoria': nome,
                'qtd': g['qtd'],
                'total_mensal': _dinheiro(g['anual'] / 12),
                'total_anual': _dinheiro(g['anual']),
                'percentual': _percentual(g['anual'], total_anual),
                'ticket_medio': _dinheiro(g['anual'] / 12 / g['qtd']),
            }
            for nome, g in sorted(grupos.items(), key=lambda kv: kv[1]['anual'], reverse=True)
        ]

    @staticmethod
    def _por_periodicidade(itens, total_anual):
        grupos = _agrupar(itens, 'periodicidade')
        return [
            {
                'periodicidade': per,
                'qtd': grupos[per]['qtd'],
                'total_mensal': _dinheiro(grupos[per]['anual'] / 12),
                'percentual': _percentual(grupos[per]['anual'], total_anual),
            }
            for per in ORDEM_PERIODICIDADE if per in grupos
        ]

    @staticmethod
    def _por_pagamento(itens, total_anual):
        grupos = _agrupar(itens, 'metodo_pagamento')
        return [
            {
                'metodo': metodo,
                'qtd': g['qtd'],
                'total_mensal': _dinheiro(g['anual'] / 12),
                'percentual': _percentual(g['anual'], total_anual),
            }
            for metodo, g in sorted(grupos.items(), key=lambda kv: kv[1]['anual'], reverse=True)
        ]

    @staticmethod
    def _faixas(itens):
        faixas = []
        for rotulo, minimo, maximo in FAIXAS_VALOR:
            qtd = sum(
                1 for i in itens
                if i['mensal'] >= minimo and (maximo is None or i['mensal'] < maximo)
            )
            faixas.append({'rotulo': rotulo, 'qtd': qtd})
        return faixas

    @staticmethod
    def _projecao(ativas, hoje, moeda_base):
        """Quanto será cobrado em cada um dos próximos 12 meses (mês atual incluso).

        Usa as datas reais de cobrança, então anuais e semanais aparecem no mês
        em que de fato caem, e não diluídos.
        """
        meses = {}
        for i in range(MESES_PROJECAO):
            meses[_somar_meses(hoje.year, hoje.month, i)] = {'total': 0.0, 'qtd': 0}

        inicio = date(hoje.year, hoje.month, 1)
        ano_fim, mes_fim = _somar_meses(hoje.year, hoje.month, MESES_PROJECAO - 1)
        fim = date(ano_fim, mes_fim, calendar.monthrange(ano_fim, mes_fim)[1])

        for a in ativas:
            valor = float(a.minha_parte_em(moeda_base))
            for data in a.renovacoes_no_periodo(inicio, fim):
                bloco = meses[(data.year, data.month)]
                bloco['total'] += valor
                bloco['qtd'] += 1

        serie = [
            {'ano': ano, 'mes': mes, 'total': _dinheiro(b['total']), 'qtd': b['qtd']}
            for (ano, mes), b in meses.items()
        ]
        total_12 = sum(m['total'] for m in serie)
        pesado = max(serie, key=lambda m: m['total'])
        leve = min(serie, key=lambda m: m['total'])

        return {
            'meses': serie,
            'total_12_meses': _dinheiro(total_12),
            'media_mensal': _dinheiro(total_12 / MESES_PROJECAO),
            'mes_mais_pesado': pesado if total_12 else None,
            'mes_mais_leve': leve if total_12 else None,
        }

    @staticmethod
    def _proximas_cobrancas(ativas, hoje, moeda_base):
        limite = max(JANELAS_COBRANCA)
        fim = hoje + timedelta(days=limite)
        cobrancas = []
        for a in ativas:
            valor = float(a.minha_parte_em(moeda_base))
            for data in a.renovacoes_no_periodo(hoje, fim):
                cobrancas.append((data, valor))

        janelas = []
        for dias in JANELAS_COBRANCA:
            corte = hoje + timedelta(days=dias)
            dentro = [valor for data, valor in cobrancas if data <= corte]
            janelas.append({'dias': dias, 'total': _dinheiro(sum(dentro)), 'qtd': len(dentro)})
        return janelas

    @staticmethod
    def _reajustes(id_usuario):
        alteracoes = HistoricoRepository.listar_alteracoes_valor(id_usuario)
        itens = []
        for historico, nome in alteracoes:
            antigo = _decimal(historico.valor_antigo)
            novo = _decimal(historico.valor_novo)
            if antigo is None or novo is None or antigo == novo:
                continue
            itens.append({
                'nome_servico': nome,
                'valor_antigo': _dinheiro(antigo),
                'valor_novo': _dinheiro(novo),
                'variacao_percentual': (
                    round(float((novo - antigo) / antigo * 100), 1) if antigo > 0 else None
                ),
                'data': historico.data_alteracao.isoformat() if historico.data_alteracao else None,
            })

        return {
            'aumentos': sum(1 for r in itens if r['valor_novo'] > r['valor_antigo']),
            'reducoes': sum(1 for r in itens if r['valor_novo'] < r['valor_antigo']),
            'recentes': itens[:MAX_REAJUSTES],
        }
