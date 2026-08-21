from werkzeug.security import generate_password_hash, check_password_hash


def hashear_senha(senha_texto_puro):
    return generate_password_hash(senha_texto_puro)


def verificar_senha(senha_texto_puro, senha_hash):
    return check_password_hash(senha_hash, senha_texto_puro)
