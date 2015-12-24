from __future__ import absolute_import, division, print_function, \
    unicode_literals
import base64
import os
from . import utils
from .utils import _


def password_derive(key):
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf import pbkdf2
    from cryptography.hazmat import backends

    kdf = pbkdf2.PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=16,
        salt=b"",
        iterations=100000,
        backend=backends.default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(key.encode('utf-8')))


class aes:
    @staticmethod
    def encrypt(str_key):
        utils.logger.debug(_("Initializing AES encryptor"))

        from cryptography.hazmat.primitives import ciphers
        from cryptography.hazmat import backends

        def func(data):
            backend = backends.default_backend()
            key = password_derive(str_key)
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
            key = password_derive(str_key)
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
