"""Ferramentas (tools) que o agente de IA pode chamar.

Cada ferramenta é só uma ponte para um service que já existe: o agente
não tem acesso ao banco nem regras próprias. Tudo passa pelas mesmas
validações da API e é sempre escopado ao usuário autenticado (o id nunca
vem da IA). Erros de negócio voltam para o modelo como {'erro': ...}
para ele se corrigir ou explicar ao usuário.
"""
import unicodedata

from app.exceptions import AppError, NotFoundError
from app.models.assinatura import Assinatura
from app.services.assinatura.atualizar_assinatura_service import AtualizarAssinaturaService
from app.services.assinatura.criar_assinatura_service import CriarAssinaturaService
from app.services.assinatura.estatisticas_assinatura_service import EstatisticasAssinaturaService
from app.services.assinatura.listar_assinaturas_service import ListarAssinaturasService
from app.services.assinatura.renovacoes_assinatura_service import RenovacoesAssinaturaService
from app.services.categoria.listar_categorias_service import ListarCategoriasService
from app.services.agente.recomendar_planos_service import RecomendarPlanosService

LIMITE_LISTAGEM = 50

_PERIODICIDADES = ['semanal', 'mensal', 'anual']
_METODOS = ['cartao_credito', 'cartao_debito', 'pix', 'boleto', 'debito_automatico', 'transferencia', 'outro']
_STATUS = ['ativa', 'pausada', 'cancelada']


def _prop(tipo, descricao, enum=None):
    p = {'type': tipo, 'description': descricao}
    if enum:
        p['enum'] = enum
    return p


_CAMPOS_ASSINATURA = {
    'nome_servico': _prop('string', 'Nome do serviço, ex.: Netflix'),
    'valor': _prop('number', 'Preço cobrado por período (não por mês), na moeda da assinatura'),
    'periodicidade': _prop('string', 'Frequência da cobrança', _PERIODICIDADES),
    'moeda': _prop('string', 'Código da moeda, ex.: BRL, USD, EUR. Padrão: moeda base do usuário'),
    'data_renovacao': _prop('string', 'Próxima cobrança no formato AAAA-MM-DD'),
    'categoria': _prop('string', 'Nome de uma categoria existente do usuário'),
    'num_pessoas': _prop('integer', 'Quantas pessoas dividem o plano, contando com o usuário'),
    'metodo_pagamento': _prop('string', 'Forma de pagamento', _METODOS),
    'tipo_plano': _prop('string', 'Nome do plano, ex.: Premium'),
}

DECLARACOES = [
    {
        'name': 'listar_assinaturas',
        'description': 'Lista as assinaturas do usuário (id, valor, periodicidade, status, próxima renovação). '
                       'Use sempre antes de alterar ou excluir, para descobrir o id correto.',
        'parameters': {'type': 'object', 'properties': {
            'busca': _prop('string', 'Parte do nome do serviço'),
            'status': _prop('string', 'Filtrar por status', _STATUS),
            'categoria': _prop('string', 'Filtrar por nome de categoria'),
        }},
    },
    {
        'name': 'listar_categorias',
        'description': 'Lista as categorias disponíveis do usuário.',
        'parameters': {'type': 'object', 'properties': {}},
    },
    {
        'name': 'resumo_gastos',
        'description': 'Resumo financeiro: total mensal e anual (parte do usuário, na moeda base), '
                       'quantidade por status e gasto por categoria.',
        'parameters': {'type': 'object', 'properties': {}},
    },
    {
        'name': 'proximas_renovacoes',
        'description': 'Próximas renovações/cobranças das assinaturas ativas, em ordem de data.',
        'parameters': {'type': 'object', 'properties': {
            'limite': _prop('integer', 'Quantidade máxima (padrão 5)'),
        }},
    },
    {
        'name': 'recomendar_planos',
        'description': 'Pesquisa na web os planos e preços atuais e sugere alternativas mais baratas '
                       '(plano anual, família, estudante, combos, promoções) para as assinaturas ativas do usuário. '
                       'Use quando ele perguntar como economizar, por planos mais baratos ou promoções. '
                       'Demora alguns segundos. Sem id_assinatura, analisa todas.',
        'parameters': {'type': 'object', 'properties': {
            'id_assinatura': _prop('integer', 'Analisar só esta assinatura (opcional)'),
        }},
    },
    {
        'name': 'criar_assinatura',
        'description': 'Cadastra uma nova assinatura para o usuário.',
        'parameters': {'type': 'object', 'properties': _CAMPOS_ASSINATURA,
                       'required': ['nome_servico', 'valor', 'categoria']},
    },
    {
        'name': 'atualizar_assinatura',
        'description': 'Altera campos de uma assinatura existente (valor, data, plano, etc.). '
                       'Também serve para pausar, cancelar ou reativar via o campo status.',
        'parameters': {'type': 'object', 'properties': {
            'id_assinatura': _prop('integer', 'Id da assinatura (obtido em listar_assinaturas)'),
            'status': _prop('string', 'Novo status', _STATUS),
            **_CAMPOS_ASSINATURA,
        }, 'required': ['id_assinatura']},
    },
    {
        'name': 'excluir_assinatura',
        'description': 'Prepara a exclusão definitiva de uma assinatura. NÃO exclui sozinho: o usuário '
                       'precisa confirmar em um botão. Para apenas encerrar, prefira atualizar_assinatura '
                       'com status cancelada.',
        'parameters': {'type': 'object', 'properties': {
            'id_assinatura': _prop('integer', 'Id da assinatura'),
        }, 'required': ['id_assinatura']},
    },
]


# ── helpers ──────────────────────────────────────────────────────

def _normalizar(valor):
    sem_acento = unicodedata.normalize('NFD', str(valor)).encode('ascii', 'ignore').decode()
    return sem_acento.lower().strip()


def _categorias_do_usuario(usuario):
    return ListarCategoriasService.executar(usuario.id_usuario)


def _resolver_categoria(nome, usuario):
    """Acha a categoria do usuário pelo nome (sem acento/maiúscula; aceita parcial)."""
    categorias = _categorias_do_usuario(usuario)
    disponiveis = [c.nome_categoria for c in categorias]
    alvo = _normalizar(nome or '')
    if alvo:
        for c in categorias:
            if _normalizar(c.nome_categoria) == alvo:
                return c, disponiveis
        for c in categorias:
            n = _normalizar(c.nome_categoria)
            if alvo in n or n in alvo:
                return c, disponiveis
    return None, disponiveis


def _assinatura_do_usuario(id_assinatura, usuario):
    """O agente só mexe nas assinaturas do próprio usuário (nem admin ganha acesso extra por aqui)."""
    try:
        id_assinatura = int(id_assinatura)
    except (TypeError, ValueError):
        raise NotFoundError('Assinatura não encontrada')
    assinatura = Assinatura.buscar_por_id(id_assinatura)
    if assinatura is None or assinatura.id_usuario != usuario.id_usuario:
        raise NotFoundError('Assinatura não encontrada')
    return assinatura


def _compacta(a, nomes_categoria):
    d = a.to_dict()
    return {
        'id_assinatura': d['id_assinatura'],
        'nome_servico': d['nome_servico'],
        'valor': d['valor_mensal'],
        'moeda': d['moeda'],
        'periodicidade': d['periodicidade'],
        'num_pessoas': d['num_pessoas'],
        'sua_parte_por_periodo': d['valor_minha_parte'],
        'status': d['status'],
        'proxima_renovacao': d['proxima_renovacao'],
        'em_teste_gratis': d['em_teste'],
        'categoria': nomes_categoria.get(d['id_categoria']),
        'plano': d['tipo_plano'],
    }


def _dados_assinatura(args, usuario):
    """Traduz os argumentos amigáveis da IA para o payload que os services já esperam."""
    dados = {}
    mapa = {'nome_servico': 'nome_servico', 'valor': 'valor_mensal', 'periodicidade': 'periodicidade',
            'moeda': 'moeda', 'data_renovacao': 'data_renovacao', 'num_pessoas': 'num_pessoas',
            'metodo_pagamento': 'metodo_pagamento', 'tipo_plano': 'tipo_plano', 'status': 'status'}
    for origem, destino in mapa.items():
        if args.get(origem) is not None:
            dados[destino] = args[origem]
    if args.get('categoria'):
        categoria, disponiveis = _resolver_categoria(args['categoria'], usuario)
        if categoria is None:
            raise _CategoriaNaoEncontrada(disponiveis)
        dados['id_categoria'] = categoria.id_categoria
    return dados


class _CategoriaNaoEncontrada(AppError):
    def __init__(self, disponiveis):
        super().__init__('Categoria não encontrada. Escolha uma das disponíveis ou pergunte ao usuário.')
        self.disponiveis = disponiveis


# ── execução ─────────────────────────────────────────────────────

def _listar_assinaturas(args, usuario, ctx):
    filtros = {'busca': args.get('busca'), 'status': args.get('status')}
    if args.get('categoria'):
        categoria, disponiveis = _resolver_categoria(args['categoria'], usuario)
        if categoria is None:
            return {'erro': 'Categoria não encontrada', 'categorias_disponiveis': disponiveis}
        filtros['id_categoria'] = categoria.id_categoria
    itens = ListarAssinaturasService.executar(usuario, filtros)
    nomes = {c.id_categoria: c.nome_categoria for c in _categorias_do_usuario(usuario)}
    return {'total': len(itens), 'assinaturas': [_compacta(a, nomes) for a in itens[:LIMITE_LISTAGEM]]}


def _listar_categorias(args, usuario, ctx):
    return {'categorias': [c.nome_categoria for c in _categorias_do_usuario(usuario)]}


def _resumo_gastos(args, usuario, ctx):
    e = EstatisticasAssinaturaService.executar(usuario)
    return {chave: e[chave] for chave in e if chave not in ('cambio',)}


def _proximas_renovacoes(args, usuario, ctx):
    itens = RenovacoesAssinaturaService.proximas(usuario, args.get('limite') or 5)
    nomes = {c.id_categoria: c.nome_categoria for c in _categorias_do_usuario(usuario)}
    return {'renovacoes': [_compacta(a, nomes) for a in itens]}


def _recomendar_planos(args, usuario, ctx):
    id_assinatura = args.get('id_assinatura')
    if id_assinatura is not None:
        id_assinatura = _assinatura_do_usuario(id_assinatura, usuario).id_assinatura
    r = RecomendarPlanosService.executar(usuario, id_assinatura)
    for fonte in r['fontes']:
        if fonte not in ctx['fontes']:
            ctx['fontes'].append(fonte)
    return {'recomendacoes': r['texto'], 'fundamentado_na_web': r['fundamentado'],
            'instrucao': 'Repasse de forma resumida e lembre o usuário de confirmar o preço no site oficial. '
                         + ('' if r['fundamentado'] else 'Avise que os valores podem estar desatualizados (sem busca na web).')}


def _criar_assinatura(args, usuario, ctx):
    dados = _dados_assinatura(args, usuario)
    assinatura = CriarAssinaturaService.executar(dados, usuario)
    ctx['acoes'].append({'tipo': 'criada', 'descricao': f'Assinatura "{assinatura.nome_servico}" criada'})
    nomes = {c.id_categoria: c.nome_categoria for c in _categorias_do_usuario(usuario)}
    return {'ok': True, 'assinatura': _compacta(assinatura, nomes)}


def _atualizar_assinatura(args, usuario, ctx):
    assinatura = _assinatura_do_usuario(args.get('id_assinatura'), usuario)
    dados = _dados_assinatura(args, usuario)
    if not dados:
        return {'erro': 'Nenhum campo para alterar foi informado'}
    assinatura = AtualizarAssinaturaService.executar(assinatura.id_assinatura, dados, usuario)
    ctx['acoes'].append({'tipo': 'atualizada', 'descricao': f'Assinatura "{assinatura.nome_servico}" atualizada'})
    nomes = {c.id_categoria: c.nome_categoria for c in _categorias_do_usuario(usuario)}
    return {'ok': True, 'assinatura': _compacta(assinatura, nomes)}


def _excluir_assinatura(args, usuario, ctx):
    assinatura = _assinatura_do_usuario(args.get('id_assinatura'), usuario)
    ctx['confirmacoes'].append({
        'tipo': 'excluir',
        'id_assinatura': assinatura.id_assinatura,
        'nome_servico': assinatura.nome_servico,
    })
    return {'status': 'aguardando_confirmacao_do_usuario',
            'instrucao': 'A exclusão AINDA NÃO foi feita. Diga ao usuário para confirmar no botão que aparece abaixo da resposta.'}


_EXECUTORES = {
    'listar_assinaturas': _listar_assinaturas,
    'listar_categorias': _listar_categorias,
    'resumo_gastos': _resumo_gastos,
    'proximas_renovacoes': _proximas_renovacoes,
    'recomendar_planos': _recomendar_planos,
    'criar_assinatura': _criar_assinatura,
    'atualizar_assinatura': _atualizar_assinatura,
    'excluir_assinatura': _excluir_assinatura,
}


def executar_ferramenta(nome, args, usuario, ctx):
    executor = _EXECUTORES.get(nome)
    if executor is None:
        return {'erro': f'Ferramenta desconhecida: {nome}'}
    if not isinstance(args, dict):
        args = {}
    try:
        return executor(args, usuario, ctx)
    except _CategoriaNaoEncontrada as erro:
        return {'erro': erro.mensagem, 'categorias_disponiveis': erro.disponiveis}
    except AppError as erro:
        return {'erro': erro.mensagem}


def resumir_assinaturas(itens, usuario):
    """Versão enxuta das assinaturas (para prompts): só o que a IA precisa."""
    nomes = {c.id_categoria: c.nome_categoria for c in _categorias_do_usuario(usuario)}
    return [_compacta(a, nomes) for a in itens]
