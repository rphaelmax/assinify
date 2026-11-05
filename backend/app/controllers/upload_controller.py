from flask import Blueprint, abort, current_app, send_from_directory

from app.armazenamento import ArmazenamentoAvatar

upload_bp = Blueprint('upload', __name__, url_prefix='/uploads')


class UploadController:
    """Entrega as fotos de perfil.

    A rota é pública de propósito: a tag <img> não envia o header
    Authorization. O nome do arquivo contém um token aleatório (não dá para
    adivinhar a URL de outra pessoa) e só nomes no formato gerado pelo
    ArmazenamentoAvatar são aceitos.
    """

    @staticmethod
    def avatar(nome):
        if not ArmazenamentoAvatar.nome_valido(nome):
            abort(404)
        resposta = send_from_directory(
            current_app.config['AVATAR_DIR'], nome, mimetype='image/jpeg', max_age=31536000
        )
        resposta.headers['X-Content-Type-Options'] = 'nosniff'
        return resposta


upload_bp.add_url_rule('/avatars/<nome>', view_func=UploadController.avatar, methods=['GET'])
