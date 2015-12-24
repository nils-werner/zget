from __future__ import absolute_import, division, print_function, \
    unicode_literals
import base64
import hashlib
import os
from . import utils
from .utils import _


class aes:
    @staticmethod
    def encrypt(str_key):
        utils.logger.debug(_("Initializing AES encryptor"))

        from cryptography.hazmat.primitives import ciphers
        from cryptography.hazmat import backends

        def func(data):
            backend = backends.default_backend()
            key = hashlib.sha256(str_key.encode('utf-8')).digest()
            iv = os.urandom(16)
            cipher = ciphers.Cipher(
                ciphers.algorithms.AES(key),
                ciphers.modes.CFB(iv),
                backend=backend,
            )
            cryptor = cipher.encryptor()
            iv_sent = False

            for raw in data:
                out = cryptor.update(raw)

                if not iv_sent:
                    out = iv + out
                    iv_sent = True

                yield out

            yield cryptor.finalize()

        func.size = lambda x: x + 16

        return func

    @staticmethod
    def decrypt(str_key):
        utils.logger.debug(_("Initializing AES decryptor"))

        from cryptography.hazmat.primitives import ciphers
        from cryptography.hazmat import backends

        def func(data):
            backend = backends.default_backend()
            key = hashlib.sha256(str_key.encode('utf-8')).digest()
            iv = None
            cipher = None
            cryptor = None

            for enc in data:
                if iv is None:
                    utils.logger.debug(
                        _("Initializing AES initialization vector")
                    )
                    iv = enc[:16]
                    enc = enc[16:]
                    cipher = ciphers.Cipher(
                        ciphers.algorithms.AES(key),
                        ciphers.modes.CFB(iv),
                        backend=backend,
                    )
                    cryptor = cipher.decryptor()
                yield cryptor.update(enc)

            yield cryptor.finalize()

        func.size = lambda x: x - 16

        return func


class bypass:
    @staticmethod
    def encrypt(key=""):
        utils.logger.debug(_("Initializing bypass cryptor"))

        def func(data):
            for chunk in data:
                yield chunk

        func.size = lambda x: x

        return func

    decrypt = encrypt
