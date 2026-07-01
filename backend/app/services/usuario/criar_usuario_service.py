from app.models.usuario import Usuario


class CriarUsuarioService:
    @staticmethod
    def executar(dados):
        if not dados.get('nome'):
            raise ValueError('Nome é obrigatório')
        if not dados.get('email'):
            raise ValueError('Email é obrigatório')
        if not dados.get('senha'):
            raise ValueError('Senha é obrigatória')

        usuario = Usuario(
            nome=dados['nome'],
            email=dados['email'],
            senha=dados['senha'],
            telefone=dados.get('telefone')
        )
        usuario.salvar()
        return usuario
