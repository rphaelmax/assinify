from app.models.usuario import Usuario


class AtualizarUsuarioService:
    @staticmethod
    def executar(id, dados):
        usuario = Usuario.buscar_por_id(id)
        if usuario is None:
            raise ValueError('Usuário não encontrado')
        usuario.atualizar(
            nome=dados.get('nome'),
            email=dados.get('email'),
            senha=dados.get('senha'),
            telefone=dados.get('telefone')
        )
        return usuario
