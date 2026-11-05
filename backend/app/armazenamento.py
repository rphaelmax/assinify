import os
import re
import uuid

from flask import current_app
from PIL import Image, ImageOps, UnidentifiedImageError

from app.exceptions import ValidationError

FORMATOS_ACEITOS = {'JPEG', 'PNG', 'WEBP'}
TAMANHO_AVATAR = 256
MAX_PIXELS = 25_000_000
NOME_VALIDO = re.compile(r'^\d+-[0-9a-f]{32}\.jpg$')


class ArmazenamentoAvatar:
    """Guarda as fotos de perfil em disco.

    A imagem enviada nunca é gravada como veio: ela é aberta, validada,
    recortada em quadrado, reduzida e regravada como JPEG. Isso descarta
    metadados (EXIF, inclusive GPS) e qualquer conteúdo que não seja imagem.
    """

    @staticmethod
    def nome_valido(nome):
        return isinstance(nome, str) and NOME_VALIDO.match(nome) is not None

    @staticmethod
    def _pasta():
        pasta = current_app.config['AVATAR_DIR']
        os.makedirs(pasta, exist_ok=True)
        return pasta

    @staticmethod
    def salvar(arquivo, id_usuario):
        """Processa o upload e devolve o nome do arquivo gravado."""
        try:
            imagem = Image.open(arquivo.stream)
            if imagem.format not in FORMATOS_ACEITOS:
                raise ValidationError('Formato não suportado. Use JPG, PNG ou WebP')
            if imagem.width * imagem.height > MAX_PIXELS:
                raise ValidationError('Imagem com dimensões grandes demais')
            imagem.load()
        except ValidationError:
            raise
        except (UnidentifiedImageError, Image.DecompressionBombError, OSError, ValueError):
            raise ValidationError('O arquivo enviado não é uma imagem válida')

        imagem = ImageOps.exif_transpose(imagem)
        if imagem.mode in ('RGBA', 'LA', 'P'):
            imagem = imagem.convert('RGBA')
            fundo = Image.new('RGB', imagem.size, (255, 255, 255))
            fundo.paste(imagem, mask=imagem.getchannel('A'))
            imagem = fundo
        else:
            imagem = imagem.convert('RGB')
        imagem = ImageOps.fit(imagem, (TAMANHO_AVATAR, TAMANHO_AVATAR), Image.LANCZOS)

        # nome novo a cada upload: evita cache de foto antiga e URL previsível
        nome = f'{id_usuario}-{uuid.uuid4().hex}.jpg'
        imagem.save(os.path.join(ArmazenamentoAvatar._pasta(), nome), 'JPEG', quality=85, optimize=True)
        return nome

    @staticmethod
    def remover(nome):
        if not ArmazenamentoAvatar.nome_valido(nome):
            return
        try:
            os.remove(os.path.join(current_app.config['AVATAR_DIR'], nome))
        except FileNotFoundError:
            pass
