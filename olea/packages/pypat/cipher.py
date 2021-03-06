__all__ = ['BaseCipher', 'aes_gcm', 'plain']

import os
from typing import Tuple

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class BaseCipher():
    is_aead = False

    class Key():
        def __init__(self, key: bytes):
            pass

        def export(self) -> bytes:
            return b''

    @staticmethod
    def encrypt(key: 'Key', data: bytes) -> Tuple[bytes, bytes]:
        return (b'', b'')

    @staticmethod
    def decrypt(key: 'Key', nonce: bytes, data: bytes) -> bytes:
        return b''


class aes_gcm(BaseCipher):
    is_aead = True

    class Key(BaseCipher.Key):
        def __init__(self, key: bytes):
            self.key = key if key else os.urandom(128 // 8)
            self.a = AESGCM(self.key)

        def export(self) -> bytes:
            return self.key

    @staticmethod
    def encrypt(key, data):
        nonce = os.urandom(12)
        return (nonce, key.a.encrypt(nonce, data, associated_data=None))

    @staticmethod
    def decrypt(key, nonce, data):
        return key.a.decrypt(nonce, data, associated_data=None)


class plain(BaseCipher):
    is_aead = False

    class Key(BaseCipher.Key):
        def export(self) -> bytes:
            return b''

    @staticmethod
    def encrypt(key, data):
        return (b'', data)

    @staticmethod
    def decrypt(key, nonce, data):
        return data
