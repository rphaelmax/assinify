class AppError(Exception):
    """Erro base da aplicação, carrega o status HTTP correspondente."""
    status_code = 400

    def __init__(self, mensagem):
        super().__init__(mensagem)
        self.mensagem = mensagem


class ValidationError(AppError):
    """Entrada inválida fornecida pelo cliente."""
    status_code = 400


class UnauthorizedError(AppError):
    """Credenciais ausentes, inválidas ou token expirado/inválido."""
    status_code = 401


class ForbiddenError(AppError):
    """Usuário autenticado, mas sem permissão para o recurso."""
    status_code = 403


class NotFoundError(AppError):
    """Recurso solicitado não existe."""
    status_code = 404
