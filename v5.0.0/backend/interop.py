import hashlib
from typing import List, Dict, Any


def sha256d(data: bytes) -> bytes:
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()


class MerkleStateTree:
    def __init__(self, leaves: List[bytes]):
        self.leaves = [sha256d(leaf) for leaf in leaves]
        if not self.leaves:
            self.leaves = [b"\x00" * 32]
        self.root = self.build_tree(self.leaves)

    def build_tree(self, nodes: List[bytes]) -> bytes:
        if len(nodes) == 1:
            return nodes[0]
        next_level = []
        for i in range(0, len(nodes), 2):
            left = nodes[i]
            right = nodes[i + 1] if i + 1 < len(nodes) else left
            next_level.append(sha256d(left + right))
        return self.build_tree(next_level)


class PartitionBridgeRouter:
    def __init__(self, partition_id: str):
        self.partition_id = partition_id
        self.inbound_receipts: Dict[str, Dict[str, Any]] = {}

    def generate_transfer_receipt(self, target_partition: str, tx_payload: bytes) -> Dict[str, Any]:
        payload_hash = sha256d(tx_payload)
        receipt_id = sha256d(
            self.partition_id.encode() + target_partition.encode() + payload_hash
        ).hex()
        return {
            "receipt_id": receipt_id,
            "source_partition": self.partition_id,
            "target_partition": target_partition,
            "commitment_hash": payload_hash.hex(),
            "status": "LOCKED",
        }

    def apply_remote_receipt(self, receipt: Dict[str, Any], proof_merkle_root: str) -> bool:
        if receipt["target_partition"] != self.partition_id:
            return False
        r_id = receipt["receipt_id"]
        if r_id in self.inbound_receipts:
            return False
        self.inbound_receipts[r_id] = {
            "receipt": receipt,
            "proof_root": proof_merkle_root,
            "status": "MINTED",
        }
        return True
