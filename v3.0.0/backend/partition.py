import hashlib
import hmac
from typing import Dict, Any


class TenantPartition:
    def __init__(self, tenant_id: str, master_secret: bytes):
        self.tenant_id = tenant_id
        self.partition_key = self._derive_partition_key(master_secret, tenant_id)
        self.state_merkle_root = hashlib.sha256(f"init:{tenant_id}".encode()).hexdigest()
        self.blocks: list = []

    @staticmethod
    def _derive_partition_key(master_secret: bytes, tenant_id: str) -> bytes:
        return hmac.new(master_secret, tenant_id.encode("utf-8"), hashlib.sha256).digest()

    def append_block(self, block_data: Dict[str, Any], block_sig: str) -> Dict[str, Any]:
        prev_hash = self.blocks[-1]["hash"] if self.blocks else "0" * 64
        block_index = len(self.blocks)

        block_record = {
            "index": block_index,
            "tenant_id": self.tenant_id,
            "prev_hash": prev_hash,
            "data": block_data,
            "signature": block_sig,
        }

        serialized = f"{block_index}:{prev_hash}:{self.tenant_id}:{block_sig}".encode()
        block_record["hash"] = hashlib.sha256(serialized).hexdigest()

        self.blocks.append(block_record)
        self.state_merkle_root = block_record["hash"]
        return block_record


class PartitionManager:
    def __init__(self, root_key: bytes):
        self.root_key = root_key
        self.partitions: Dict[str, TenantPartition] = {}

    def get_or_create(self, tenant_id: str) -> TenantPartition:
        if tenant_id not in self.partitions:
            self.partitions[tenant_id] = TenantPartition(tenant_id, self.root_key)
        return self.partitions[tenant_id]
