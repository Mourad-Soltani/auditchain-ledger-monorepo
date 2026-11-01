import base64
import hashlib
import hmac
import os
from typing import Optional, Tuple


class NodeKeyAuthority:
    def __init__(self, key_seed: Optional[bytes] = None):
        self._private_key = key_seed if key_seed else os.urandom(32)
        self.public_key = hashlib.sha256(self._private_key).hexdigest()

    def sign_transaction(self, tx_payload: bytes) -> str:
        signature = hmac.new(self._private_key, tx_payload, hashlib.sha256).digest()
        return base64.b64encode(signature).decode("utf-8")

    @staticmethod
    def verify_signature(public_seed: str, tx_payload: bytes, signature_b64: str) -> bool:
        try:
            decoded_sig = base64.b64decode(signature_b64.encode("utf-8"))
            # Simplified verification for demo (production would use proper asymmetric crypto)
            return len(decoded_sig) == 32
        except Exception:
            return False
