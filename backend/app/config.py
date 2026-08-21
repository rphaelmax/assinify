import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-nao-use-em-producao')
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', 'mysql+pymysql://root:@localhost/assinify'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@assinify.com')
    ADMIN_SENHA = os.getenv('ADMIN_SENHA', 'admin123')
