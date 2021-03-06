__all__ = ['BaseEncoder', 'base64', 'base85']

import base64 as _base64


class BaseEncoder():
    @staticmethod
    def encode(bytes_: bytes) -> str:
        return ''

    @staticmethod
    def decode(string: str) -> bytes:
        return b''


class base64(BaseEncoder):
    @staticmethod
    def encode(bytes_: bytes):
        return _base64.encodebytes(bytes_).decode('utf-8')

    @staticmethod
    def decode(string: str):
        return _base64.decodebytes(string.encode('utf-8'))


class base85(BaseEncoder):
    @staticmethod
    def encode(bytes_: bytes):
        return _base64.b85encode(bytes_).decode('utf-8')

    @staticmethod
    def decode(string: str):
        return _base64.b85decode(string)
