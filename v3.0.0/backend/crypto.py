import hmac
import hashlib
import base64
from typing import Union


class CryptoEngine:
    @staticmethod
    def sign_hmac_sha256(key: bytes, message: bytes) -> str:
        h = hmac.new(key, message, hashlib.sha256)
        return base64.b64encode(h.digest()).decode("utf-8")

    @staticmethod
    def verify_hmac_sha256(key: bytes, message: bytes, signature_b64: str) -> bool:
        try:
            signature = base64.b64decode(signature_b64.encode("utf-8"))
            expected = hmac.new(key, message, hashlib.sha256).digest()
            return hmac.compare_digest(signature, expected)
        except Exception:
            return False

    @staticmethod
    def hash_leaf(data: Union[str, bytes]) -> str:
        if isinstance(data, str):
            data = data.encode("utf-8")
        return hashlib.sha256(data).hexdigest()
