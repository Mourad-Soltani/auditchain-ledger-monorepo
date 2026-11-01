import hashlib
import json
import os
import threading
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from backend.config import GENESIS_PREV_HASH, LEDGER_STORAGE_PATH


class Block:
    def __init__(
        self,
        index: int,
        timestamp: str,
        event_type: str,
        actor: str,
        data: Dict[str, Any],
        prev_hash: str,
        block_hash: Optional[str] = None,
    ):
        self.index = index
        self.timestamp = timestamp
        self.event_type = event_type
        self.actor = actor
        self.data = data
        self.prev_hash = prev_hash
        self.hash = block_hash if block_hash else self.calculate_hash()

    def payload(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "actor": self.actor,
            "data": self.data,
            "prev_hash": self.prev_hash,
        }

    def calculate_hash(self) -> str:
        canonical_json = json.dumps(self.payload(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        result = self.payload()
        result["hash"] = self.hash
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Block":
        return cls(
            index=data["index"],
            timestamp=data["timestamp"],
            event_type=data["event_type"],
            actor=data["actor"],
            data=data["data"],
            prev_hash=data["prev_hash"],
            block_hash=data["hash"],
        )


class AuditLedger:
    def __init__(self, storage_path: str = LEDGER_STORAGE_PATH):
        self.storage_path = storage_path
        self.chain: List[Block] = []
        self.lock = threading.Lock()
        self.load_or_initialize()

    def create_genesis_block(self) -> Block:
        ts = datetime.now(timezone.utc).isoformat()
        return Block(
            index=0,
            timestamp=ts,
            event_type="GENESIS",
            actor="SYSTEM",
            data={"message": "AuditChain Genesis Block Initialized"},
            prev_hash=GENESIS_PREV_HASH,
        )

    def load_or_initialize(self) -> None:
        with self.lock:
            if os.path.exists(self.storage_path):
                try:
                    with open(self.storage_path, "r", encoding="utf-8") as f:
                        raw_chain = json.load(f)
                        self.chain = [Block.from_dict(b) for b in raw_chain]
                        return
                except (json.JSONDecodeError, KeyError):
                    pass
            self.chain = [self.create_genesis_block()]
            self._persist()

    def _persist(self) -> None:
        dirname = os.path.dirname(self.storage_path)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        temp_file = f"{self.storage_path}.tmp"
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump([b.to_dict() for b in self.chain], f, indent=2)
        os.replace(temp_file, self.storage_path)

    def append_event(self, event_type: str, actor: str, data: Dict[str, Any]) -> Block:
        with self.lock:
            prev_block = self.chain[-1]
            block = Block(
                index=len(self.chain),
                timestamp=datetime.now(timezone.utc).isoformat(),
                event_type=event_type,
                actor=actor,
                data=data,
                prev_hash=prev_block.hash,
            )
            self.chain.append(block)
            self._persist()
            return block

    def verify_integrity(self) -> Tuple[bool, Optional[str]]:
        with self.lock:
            if not self.chain:
                return False, "Chain is completely empty."
            genesis = self.chain[0]
            if genesis.index != 0 or genesis.prev_hash != GENESIS_PREV_HASH:
                return False, "Invalid genesis block metadata."
            if genesis.hash != genesis.calculate_hash():
                return False, "Genesis block hash mismatch at index 0."
            for i in range(1, len(self.chain)):
                curr = self.chain[i]
                prev = self.chain[i - 1]
                if curr.index != i:
                    return False, f"Index sequence broken at block {i}."
                if curr.prev_hash != prev.hash:
                    return False, f"Hash chain pointer broken between blocks {i - 1} and {i}."
                if curr.hash != curr.calculate_hash():
                    return False, f"Tampered payload detected at block index {i}."
            return True, None
