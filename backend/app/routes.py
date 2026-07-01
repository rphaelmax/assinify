from app.controllers.usuario_controller import UsuarioController
from app.controllers.categoria_controller import CategoriaController
from app.controllers.assinatura_controller import AssinaturaController


def registrar_rotas(app):
    app.add_url_rule('/usuarios', endpoint='usuario_criar', view_func=UsuarioController.criar, methods=['POST'])
    app.add_url_rule('/usuarios', endpoint='usuario_listar', view_func=UsuarioController.listar, methods=['GET'])
    app.add_url_rule('/usuarios/<int:id>', endpoint='usuario_buscar', view_func=UsuarioController.buscar, methods=['GET'])
    app.add_url_rule('/usuarios/<int:id>', endpoint='usuario_atualizar', view_func=UsuarioController.atualizar, methods=['PUT'])
    app.add_url_rule('/usuarios/<int:id>', endpoint='usuario_deletar', view_func=UsuarioController.deletar, methods=['DELETE'])

    app.add_url_rule('/categorias', endpoint='categoria_criar', view_func=CategoriaController.criar, methods=['POST'])
    app.add_url_rule('/categorias', endpoint='categoria_listar', view_func=CategoriaController.listar, methods=['GET'])
    app.add_url_rule('/categorias/<int:id>', endpoint='categoria_buscar', view_func=CategoriaController.buscar, methods=['GET'])
    app.add_url_rule('/categorias/<int:id>', endpoint='categoria_atualizar', view_func=CategoriaController.atualizar, methods=['PUT'])
    app.add_url_rule('/categorias/<int:id>', endpoint='categoria_deletar', view_func=CategoriaController.deletar, methods=['DELETE'])

    app.add_url_rule('/assinaturas', endpoint='assinatura_criar', view_func=AssinaturaController.criar, methods=['POST'])
    app.add_url_rule('/assinaturas', endpoint='assinatura_listar', view_func=AssinaturaController.listar, methods=['GET'])
    app.add_url_rule('/assinaturas/<int:id>', endpoint='assinatura_buscar', view_func=AssinaturaController.buscar, methods=['GET'])
    app.add_url_rule('/assinaturas/<int:id>', endpoint='assinatura_atualizar', view_func=AssinaturaController.atualizar, methods=['PUT'])
    app.add_url_rule('/assinaturas/<int:id>', endpoint='assinatura_deletar', view_func=AssinaturaController.deletar, methods=['DELETE'])