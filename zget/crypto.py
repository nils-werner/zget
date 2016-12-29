from __future__ import absolute_import, division, print_function, \
    unicode_literals
import itertools
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
    return base64.urlsafe_b64encode(kdf.derive(key))


class aes(object):
    class encrypt(object):
        def __init__(self, str_key):
            utils.logger.debug(_("Initializing AES encryptor"))

            from cryptography.hazmat import backends

            self.backend = backends.default_backend()
            self.key = None
            self.iv = None
            self.salt = None
            self.hmac_salt = None
            self.cipher = None
            self.cryptor = None
            self.str_key = str_key.encode()
            self.iv_sent = False

        def __call__(self, data):
            from cryptography.hazmat.primitives import ciphers, hmac, hashes

            self.salt = os.urandom(16)
            self.hmac_salt = os.urandom(16)
            self.iv = os.urandom(16)
            self.key = password_derive(self.str_key, self.salt)
            self.hmac_key = password_derive(self.str_key, self.hmac_salt)
            del self.str_key
            self.h = hmac.HMAC(
                self.hmac_key,
                hashes.SHA256(),
                backend=self.backend
            )
            self.cipher = ciphers.Cipher(
                ciphers.algorithms.AES(self.key),
                ciphers.modes.CTR(self.iv),
                backend=self.backend,
            )
            self.cryptor = self.cipher.encryptor()

            for raw in data:
                out = self.cryptor.update(raw)

                if not self.iv_sent:
                    out = self.iv + self.salt + self.hmac_salt + out
                    self.iv_sent = True

                self.h.update(out)

                yield out

            out = self.cryptor.finalize()
            self.h.update(out)
            yield out

            signature = self.h.finalize()
            yield signature

        def size(self, x):
            return x + 80   # iv, salts and signature are 80 bytes

    class decrypt(object):
        def __init__(self, str_key):
            utils.logger.debug(_("Initializing AES decryptor"))

            from cryptography.hazmat import backends

            self.backend = backends.default_backend()
            self.key = None
            self.iv = None
            self.salt = None
            self.hmac_salt = None
            self.cipher = None
            self.cryptor = None
            self.str_key = str_key.encode()

        def __call__(self, data):
            from cryptography.hazmat.primitives import ciphers, hmac, hashes
            import cryptography.exceptions

            # ensure minimum chunksize of 32 so we can easily read signature
            # iterate pairwise to detect last chunk and verify HMAC
            for enc, nextenc in utils.pairwise(utils.minimum_chunksize(data)):
                if self.iv is None:
                    utils.logger.debug(
                        _("Initializing AES initialization vector")
                    )
                    self.iv = enc[:16]
                    self.salt = enc[16:32]
                    self.hmac_salt = enc[32:48]
                    self.key = password_derive(self.str_key, self.salt)
                    self.hmac_key = password_derive(
                        self.str_key, self.hmac_salt
                    )
                    del self.str_key
                    self.h = hmac.HMAC(
                        self.hmac_key,
                        hashes.SHA256(),
                        backend=self.backend
                    )
                    self.cipher = ciphers.Cipher(
                        ciphers.algorithms.AES(self.key),
                        ciphers.modes.CTR(self.iv),
                        backend=self.backend,
                    )
                    self.cryptor = self.cipher.decryptor()
                    self.h.update(self.iv + self.salt + self.hmac_salt)

                    enc = enc[48:]

                if nextenc is None:
                    signature = enc[-32:]
                    enc = enc[:-32]
                    self.h.update(enc)
                    try:
                        self.h.verify(signature)
                    except cryptography.exceptions.InvalidSignature:
                        raise RuntimeError(
                            _("File decryption failed. Did you supply the "
                              "correct password?")
                            )
                else:
                    self.h.update(enc)

                yield self.cryptor.update(enc)

            yield self.cryptor.finalize()

        def size(self, x):
            return x - 80   # iv, salts and signature are 80 bytes


class bypass(object):
    class encrypt(object):
        def __init__(self, key=""):
            utils.logger.debug(_("Initializing bypass cryptor"))

        def __call__(self, data):
            for chunk in data:
                yield chunk

        def size(self, x):
            return x

    decrypt = encrypt
