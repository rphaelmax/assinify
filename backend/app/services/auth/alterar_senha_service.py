from app.security.senha import verificar_senha, hashear_senha
from app.exceptions import ValidationError
from app.validacao import validar_forca_senha


SENHA_MIN = 6


class AlterarSenhaService:
    """Troca a senha do usuário autenticado após validar a senha atual."""

    @staticmethod
    def executar(dados, usuario_atual):
        senha_atual = dados.get('senha_atual')
        nova_senha = dados.get('nova_senha')

        if not isinstance(senha_atual, str) or not senha_atual:
            raise ValidationError('Senha atual é obrigatória')
        if not isinstance(nova_senha, str) or len(nova_senha) < SENHA_MIN:
            raise ValidationError(f'Nova senha deve ter ao menos {SENHA_MIN} caracteres')
        validar_forca_senha(nova_senha, minimo_nivel=1)

        if not verificar_senha(senha_atual, usuario_atual.senha_hash):
            raise ValidationError('Senha atual incorreta')

        if senha_atual == nova_senha:
            raise ValidationError('A nova senha deve ser diferente da atual')

        usuario_atual.atualizar(senha_hash=hashear_senha(nova_senha))
        return usuario_atual
