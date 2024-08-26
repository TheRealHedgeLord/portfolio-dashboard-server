import hashlib
import base64
import json

from cryptography.fernet import Fernet


class AccountCipher:
    def __init__(self, passphrase: str) -> None:
        self.cipher = Fernet(
            base64.b64encode(hashlib.sha256(passphrase.encode()).digest())
        )

    def encrypt(self, account: str | dict) -> bytes:
        if isinstance(account, str):
            return self.cipher.encrypt(b"\x00" + account.encode())
        else:
            return self.cipher.encrypt(b"\x01" + json.dumps(account).encode())

    def decrypt(self, secret: bytes) -> str | dict:
        decrypted = self.cipher.decrypt(secret)
        if decrypted[0] == 0:
            return decrypted[1::].decode()
        else:
            return json.loads(decrypted[1::])
