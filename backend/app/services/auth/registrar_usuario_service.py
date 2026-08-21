from app.models.usuario import Usuario
from app.repositories.usuario_repository import UsuarioRepository
from app.security.senha import hashear_senha
from app.exceptions import ValidationError
from app.models.categoria import Categoria

CATEGORIAS_PADRAO = [
    ('Entretenimento', 'Streaming, filmes, séries e conteúdo digital.'),
    ('Música', 'Serviços de música e áudio.'),
    ('Software', 'Aplicativos, ferramentas e serviços SaaS.'),
    ('Educação', 'Cursos, plataformas de estudo e aprendizado.'),
    ('Jogos', 'Jogos, assinaturas de consoles e serviços gamer.'),
    ('Armazenamento', 'Nuvem, backup e armazenamento de arquivos.'),
    ('Produtividade', 'Ferramentas pessoais e profissionais.'),
    ('Outros', 'Assinaturas que não se encaixam nas categorias anteriores.'),
]

SENHA_MIN_CARACTERES = 6


class RegistrarUsuarioService:
    """Cadastro público de usuário. Sempre cria com role='user' — ninguém
    se autopromove a admin por aqui."""

    @staticmethod
    def executar(dados):
        nome = dados.get('nome')
        email = dados.get('email')
        senha = dados.get('senha')

        if not nome:
            raise ValidationError('Nome é obrigatório')
        if not email:
            raise ValidationError('Email é obrigatório')
        if not senha or len(senha) < SENHA_MIN_CARACTERES:
            raise ValidationError(
                f'Senha é obrigatória e deve ter ao menos {SENHA_MIN_CARACTERES} caracteres'
            )

        if UsuarioRepository.buscar_por_email(email) is not None:
            raise ValidationError('Já existe um usuário cadastrado com esse email')

        usuario = Usuario(
            nome=nome,
            email=email,
            senha_hash=hashear_senha(senha),
            role='user'
        )
        usuario.salvar()

        for nome_categoria, descricao in CATEGORIAS_PADRAO:
            Categoria(
                nome_categoria=nome_categoria,
                descricao=descricao,
                id_usuario=usuario.id_usuario
            ).salvar()

        return usuario
