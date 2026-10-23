import re
from datetime import date
from decimal import Decimal, InvalidOperation

from app.exceptions import ValidationError

EMAIL_REGEX = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
VALOR_MAXIMO = Decimal('99999999.99')


def texto(valor, campo, maximo, obrigatorio=True):
    if valor is None:
        if obrigatorio:
            raise ValidationError(f'{campo} é obrigatório')
        return None
    if not isinstance(valor, str):
        raise ValidationError(f'{campo} inválido')
    valor = valor.strip()
    if not valor:
        if obrigatorio:
            raise ValidationError(f'{campo} é obrigatório')
        return valor
    if len(valor) > maximo:
        raise ValidationError(f'{campo} deve ter no máximo {maximo} caracteres')
    return valor


def validar_email(valor):
    valor = texto(valor, 'Email', 120)
    if not EMAIL_REGEX.match(valor):
        raise ValidationError('Email inválido')
    return valor


def valor_monetario(valor):
    if valor is None:
        raise ValidationError('Valor mensal é obrigatório')
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValidationError('Valor mensal inválido')
    try:
        decimal = Decimal(str(valor)).quantize(Decimal('0.01'))
    except InvalidOperation:
        raise ValidationError('Valor mensal inválido')
    if not decimal.is_finite():
        raise ValidationError('Valor mensal inválido')
    if decimal <= 0:
        raise ValidationError('Valor mensal deve ser maior que zero')
    if decimal > VALOR_MAXIMO:
        raise ValidationError('Valor mensal acima do limite permitido')
    return decimal


def data_iso(valor, campo):
    if not valor:
        raise ValidationError(f'{campo} é obrigatória')
    if not isinstance(valor, str):
        raise ValidationError(f'{campo} inválida')
    try:
        return date.fromisoformat(valor)
    except ValueError:
        raise ValidationError(f'{campo} inválida')


def exigir_id_categoria(valor):
    if not valor:
        raise ValidationError('Categoria é obrigatória')
    if isinstance(valor, bool) or not isinstance(valor, int) or valor < 1:
        raise ValidationError('Categoria inválida')
    return valor


PERIODICIDADES_VALIDAS = {'semanal', 'mensal', 'anual'}


def validar_forca_senha(senha, minimo_nivel=1):
    """Valida força mínima da senha (0-4). Nível 0 = muito fraca, bloqueia."""
    if not isinstance(senha, str) or not senha:
        raise ValidationError('Senha é obrigatória')
    score = 0
    if len(senha) >= 6:
        score += 1
    if len(senha) >= 10:
        score += 1
    import re as _re
    tem_maiuscula = bool(_re.search(r'[A-Z]', senha))
    tem_minuscula = bool(_re.search(r'[a-z]', senha))
    tem_digito = bool(_re.search(r'\d', senha))
    tem_simbolo = bool(_re.search(r'[^A-Za-z0-9]', senha))
    if tem_maiuscula and tem_minuscula:
        score += 1
    if tem_digito:
        score += 1
    if tem_simbolo:
        score += 1
    # Penaliza senhas triviais: repetição ou sequências óbvias no início
    if _re.match(r'^(.)\1+$', senha) or _re.match(r'^(123|abc|qwerty)', senha, _re.IGNORECASE):
        score = min(score, 1)
    # Senhas com apenas um tipo de caractere (só letras minúsculas, só dígitos etc.) ficam no nível 0
    tipos = sum([tem_maiuscula or tem_minuscula, tem_digito, tem_simbolo])
    # Se só tem 1 tipo e não tem mix de caixa, força nível 0
    if tipos <= 1 and not (tem_maiuscula and tem_minuscula):
        score = min(score, 0)
    nivel = min(score, 4)
    if nivel < minimo_nivel:
        raise ValidationError('Senha muito fraca. Use letras maiúsculas, números e símbolos para fortalecer.')
    return senha


def validar_periodicidade(valor):
    if valor is None or valor == '':
        return 'mensal'
    if not isinstance(valor, str) or valor not in PERIODICIDADES_VALIDAS:
        raise ValidationError('Periodicidade inválida. Use: semanal, mensal ou anual')
    return valor