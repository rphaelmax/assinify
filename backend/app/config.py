import os
from dotenv import load_dotenv

load_dotenv()


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
AVATAR_MAX_BYTES = 2 * 1024 * 1024
# Versão vigente dos Termos de Uso / Política de Privacidade (frontend/pages/termos.html).
# Ao publicar uma nova versão dos termos, atualize aqui e na página.
TERMOS_VERSAO = '1.0'


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-nao-use-em-producao')
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', 'mysql+pymysql://root:@localhost/assinify'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Fotos de perfil: ficam em disco; no banco vai só o nome do arquivo.
    AVATAR_DIR = os.getenv('AVATAR_DIR', os.path.join(BASE_DIR, 'uploads', 'avatars'))
    AVATAR_MAX_BYTES = AVATAR_MAX_BYTES
    # margem para o overhead do multipart; o limite real da imagem é AVATAR_MAX_BYTES
    MAX_CONTENT_LENGTH = AVATAR_MAX_BYTES + 100 * 1024

    TERMOS_VERSAO = TERMOS_VERSAO

    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@assinify.com')
    ADMIN_SENHA = os.getenv('ADMIN_SENHA', 'admin123')

    # Agente de IA (Gemini). Sem GEMINI_API_KEY o endpoint /agente responde 503.
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-3.5-flash')
    GEMINI_MODEL_FALLBACK = os.getenv('GEMINI_MODEL_FALLBACK', 'gemini-2.5-flash')
