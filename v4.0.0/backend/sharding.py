import bisect
import hashlib
from typing import Dict, List, Optional


class ConsistentHashRing:
    def __init__(self, replicas: int = 128):
        self.replicas = replicas
        self.ring: List[int] = []
        self.ring_map: Dict[int, str] = {}
        self.physical_nodes: set = set()

    def _hash(self, key: str) -> int:
        digest = hashlib.md5(key.encode("utf-8")).hexdigest()
        return int(digest, 16)

    def add_node(self, node: str) -> None:
        self.physical_nodes.add(node)
        for i in range(self.replicas):
            vnode_key = f"{node}#vn_{i}"
            val = self._hash(vnode_key)
            bisect.insort(self.ring, val)
            self.ring_map[val] = node

    def remove_node(self, node: str) -> None:
        if node not in self.physical_nodes:
            return
        self.physical_nodes.remove(node)
        for i in range(self.replicas):
            vnode_key = f"{node}#vn_{i}"
            val = self._hash(vnode_key)
            idx = bisect.bisect_left(self.ring, val)
            if idx < len(self.ring) and self.ring[idx] == val:
                del self.ring[idx]
            self.ring_map.pop(val, None)

    def get_node(self, partition_key: str) -> Optional[str]:
        if not self.ring:
            return None
        val = self._hash(partition_key)
        idx = bisect.bisect_right(self.ring, val)
        if idx == len(self.ring):
            idx = 0
        return self.ring_map[self.ring[idx]]
