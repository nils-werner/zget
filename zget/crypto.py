from __future__ import absolute_import, division, print_function, \
    unicode_literals
import base64
import hashlib
import os
from . import utils
from .utils import _


class aes:
    class encrypt:
        def __init__(self, key):
            utils.logger.debug(_("Initializing AES encryptor"))

            from cryptography.hazmat.primitives import ciphers
            from cryptography.hazmat import backends

            self.backend = backends.default_backend()
            self.key = hashlib.sha256(key.encode('utf-8')).digest()
            self.iv = os.urandom(16)
            self.cipher = ciphers.Cipher(
                ciphers.algorithms.AES(self.key),
                ciphers.modes.CFB(self.iv),
                backend=self.backend,
            )
            self.cryptor = self.cipher.encryptor()
            self.iv_sent = False

        def process(self, raw):
            out = self.cryptor.update(raw)

            if not self.iv_sent:
                out = self.iv + out
                self.iv_sent = True

            return out

        def finalize(self):
            return self.cryptor.finalize()

        def size(self, sizein):
            return sizein + 16

    class decrypt:
        def __init__(self, key):
            utils.logger.debug(_("Initializing AES decryptor"))

            self.key = hashlib.sha256(key.encode('utf-8')).digest()
            self.iv = None

        def process(self, enc):
            if self.iv is None:
                utils.logger.debug(_("Initializing AES initialization vector"))

                from cryptography.hazmat.primitives import ciphers
                from cryptography.hazmat import backends

                self.backend = backends.default_backend()
                self.iv = enc[:16]
                enc = enc[16:]
                self.cipher = ciphers.Cipher(
                    ciphers.algorithms.AES(self.key),
                    ciphers.modes.CFB(self.iv),
                    backend=self.backend,
                )
                self.cryptor = self.cipher.decryptor()

            out = self.cryptor.update(enc)

            return out

        def finalize(self):
            return self.cryptor.finalize()


class bypass:
    class encrypt:
        def __init__(self, key=""):
            utils.logger.debug(_("Initializing bypass cryptor"))

        def process(self, raw):
            return raw

        def finalize(self):
            return b""

        def size(self, sizein):
            return sizein

    decrypt = encrypt
