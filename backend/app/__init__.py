from flask import Flask
from flask_cors import CORS
from app.extensions import db
from app.routes import registrar_rotas


def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = (
        'mysql+pymysql://root:@localhost/assinify'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'assinify-secret'

    CORS(app)
    db.init_app(app)
    registrar_rotas(app)

    return app
