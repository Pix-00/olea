import os
from abc import ABC, abstractmethod, abstractstaticmethod

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

__all__ = ['BaseCipher', 'aes_gcm', 'plain']


class BaseCipher(ABC):
    is_aead = None

    class Key(ABC):
        @abstractmethod
        def __init__(self, key: bytes):
            pass

        @abstractmethod
        def export(self) -> bytes:
            return b''

    @abstractstaticmethod
    def encrypt(key: 'BaseCipher.Key', data: bytes) -> bytes:
        return b''

    @abstractstaticmethod
    def decrypt(key: 'BaseCipher.Key', nonce: bytes, data: bytes) -> bytes:
        return b''


class aes_gcm(BaseCipher):
    is_aead = True

    class Key(BaseCipher.Key):
        def __init__(self, key: bytes = os.urandom(128 // 8)):
            self.key = key
            self.a = AESGCM(key)

        def export(self) -> bytes:
            return self.key

    @staticmethod
    def encrypt(key, data):
        nonce = os.urandom(12)
        return nonce, key.a.encrypt(nonce, data, associated_data=None)

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
        return b'', data

    @staticmethod
    def decrypt(key, nonce, data):
        return data
