import hashlib
import json
import logging
from typing import Dict, List, Optional

logger = logging.getLogger("AuditChain.Healing")


class AutoHealingEngine:
    def __init__(self, cluster_rpc_client=None):
        self.client = cluster_rpc_client

    @staticmethod
    def compute_block_hash(block: Dict) -> str:
        block_copy = {k: v for k, v in block.items() if k != "hash"}
        serialized = json.dumps(block_copy, sort_keys=True).encode()
        return hashlib.sha256(serialized).hexdigest()

    def audit_chain_integrity(self, chain: List[Dict]) -> List[int]:
        corrupted_indices = []
        for i in range(len(chain)):
            expected_hash = self.compute_block_hash(chain[i])
            if chain[i].get("hash") != expected_hash:
                corrupted_indices.append(i)
                continue
            if i > 0 and chain[i].get("prev_hash") != chain[i - 1].get("hash"):
                corrupted_indices.append(i)
        return corrupted_indices

    async def repair_corrupted_blocks(self, chain: List[Dict], peer_nodes: List[str]) -> List[Dict]:
        corrupted_indices = self.audit_chain_integrity(chain)
        if not corrupted_indices:
            return chain
        for idx in corrupted_indices:
            logger.warning(f"Tamper detected at block index {idx}. Requesting quorum repair...")
            if self.client:
                valid_block = await self.client.fetch_block_from_peers(idx, peer_nodes)
                if valid_block and self.compute_block_hash(valid_block) == valid_block.get("hash"):
                    chain[idx] = valid_block
                    logger.info(f"Block index {idx} restored to valid cryptographic state.")
                else:
                    logger.error(f"Failed to restore block {idx} across quorum peers.")
        return chain
