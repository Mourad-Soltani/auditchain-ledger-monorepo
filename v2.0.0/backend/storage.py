import os
import json
from typing import List, Dict, Any, Optional
from backend.merkle import MerkleTree


class LedgerStorage:
    def __init__(self, filepath: str = "ledger_store.jsonl"):
        self.filepath = filepath
        self._records: List[Dict[str, Any]] = []
        self._tree: Optional[MerkleTree] = None
        self.load_and_sync()

    def load_and_sync(self) -> None:
        self._records = []
        if os.path.exists(self.filepath):
            with open(self.filepath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        self._records.append(json.loads(line))
        self._rebuild_tree()

    def _rebuild_tree(self) -> None:
        serialized = [json.dumps(r, sort_keys=True) for r in self._records]
        self._tree = MerkleTree(serialized)

    def append_record(self, record: Dict[str, Any]) -> int:
        with open(self.filepath, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, sort_keys=True) + "\n")
        self._records.append(record)
        self._rebuild_tree()
        return len(self._records) - 1

    def append_batch(self, batch: List[Dict[str, Any]]) -> List[int]:
        indices = []
        start_idx = len(self._records)
        with open(self.filepath, "a", encoding="utf-8") as f:
            for i, record in enumerate(batch):
                f.write(json.dumps(record, sort_keys=True) + "\n")
                self._records.append(record)
                indices.append(start_idx + i)
        self._rebuild_tree()
        return indices

    @property
    def current_root(self) -> Optional[str]:
        return self._tree.root if self._tree else None

    def get_proof_for_record(self, index: int) -> Dict[str, Any]:
        if not self._tree or index < 0 or index >= len(self._records):
            raise IndexError("Index out of bounds")
        proof = self._tree.get_proof(index)
        return {
            "index": index,
            "record": self._records[index],
            "leaf_hash": self._tree.hash_leaf(json.dumps(self._records[index], sort_keys=True)),
            "root": self._tree.root,
            "proof": proof
        }
