from __future__ import absolute_import, division, print_function, \
    unicode_literals
import base64
import os
from . import utils
from .utils import _


def password_derive(key, salt):
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf import pbkdf2
    from cryptography.hazmat import backends

    kdf = pbkdf2.PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=16,
        salt=salt,
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
            salt = os.urandom(16)
            iv = os.urandom(16)
            key = password_derive(str_key, salt)
            cipher = ciphers.Cipher(
                ciphers.algorithms.AES(key),
                ciphers.modes.CTR(iv),
                backend=backend,
            )
            cryptor = cipher.encryptor()
            iv_sent = False

            for raw in data:
                out = cryptor.update(raw)

                if not iv_sent:
                    out = iv + salt + out
                    iv_sent = True

                yield out

            yield cryptor.finalize()

        func.size = lambda x: x + 32   # iv and salt are 32 bytes

        return func

    @staticmethod
    def decrypt(str_key):
        utils.logger.debug(_("Initializing AES decryptor"))

        from cryptography.hazmat.primitives import ciphers
        from cryptography.hazmat import backends

        def func(data):
            backend = backends.default_backend()
            key = None
            iv = None
            salt = None
            cipher = None
            cryptor = None

            for enc in data:
                if iv is None:
                    utils.logger.debug(
                        _("Initializing AES initialization vector")
                    )
                    iv = enc[:16]
                    salt = enc[16:32]
                    enc = enc[32:]
                    key = password_derive(str_key, salt)
                    cipher = ciphers.Cipher(
                        ciphers.algorithms.AES(key),
                        ciphers.modes.CTR(iv),
                        backend=backend,
                    )
                    cryptor = cipher.decryptor()
                yield cryptor.update(enc)

            yield cryptor.finalize()

        func.size = lambda x: x - 32   # iv and salt are 32 bytes

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
