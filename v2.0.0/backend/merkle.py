import hashlib
from typing import List, Dict, Any, Optional

LEAF_PREFIX = b"\x00"
INTERNAL_PREFIX = b"\x01"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class MerkleTree:
    def __init__(self, leaves: Optional[List[str]] = None):
        self.raw_leaves: List[str] = leaves or []
        self.levels: List[List[str]] = []
        if self.raw_leaves:
            self.build_tree()

    def hash_leaf(self, leaf_data: str) -> str:
        return sha256(LEAF_PREFIX + leaf_data.encode("utf-8"))

    def hash_nodes(self, left: str, right: str) -> str:
        combined = INTERNAL_PREFIX + bytes.fromhex(left) + bytes.fromhex(right)
        return sha256(combined)

    def build_tree(self) -> None:
        if not self.raw_leaves:
            self.levels = [[]]
            return

        current_level = [self.hash_leaf(l) for l in self.raw_leaves]
        self.levels = [current_level]

        while len(current_level) > 1:
            next_level: List[str] = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left
                next_level.append(self.hash_nodes(left, right))
            current_level = next_level
            self.levels.append(current_level)

    @property
    def root(self) -> Optional[str]:
        if not self.levels or not self.levels[-1]:
            return None
        return self.levels[-1][0]

    def get_proof(self, index: int) -> List[Dict[str, str]]:
        if index < 0 or index >= len(self.raw_leaves):
            raise IndexError("Leaf index out of bounds")

        proof: List[Dict[str, str]] = []
        idx = index
        for level in self.levels[:-1]:
            is_right_child = (idx % 2 == 1)
            sibling_idx = idx - 1 if is_right_child else idx + 1

            if sibling_idx < len(level):
                sibling_hash = level[sibling_idx]
            else:
                sibling_hash = level[idx]

            proof.append({
                "position": "left" if is_right_child else "right",
                "hash": sibling_hash
            })
            idx //= 2

        return proof

    @staticmethod
    def verify_proof(leaf_data: str, proof: List[Dict[str, str]], root: str) -> bool:
        current_hash = sha256(LEAF_PREFIX + leaf_data.encode("utf-8"))
        for step in proof:
            sibling_hash = step["hash"]
            if step["position"] == "left":
                current_hash = sha256(INTERNAL_PREFIX + bytes.fromhex(sibling_hash) + bytes.fromhex(current_hash))
            else:
                current_hash = sha256(INTERNAL_PREFIX + bytes.fromhex(current_hash) + bytes.fromhex(sibling_hash))
        return current_hash == root
