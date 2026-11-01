import hashlib
import json
import logging
import time
from typing import Dict, List, Optional

logger = logging.getLogger("AuditChain.Consensus")


class NodeRole:
    FOLLOWER = "FOLLOWER"
    CANDIDATE = "CANDIDATE"
    LEADER = "LEADER"


class RaftConsensusEngine:
    def __init__(self, node_id: str, peers: List[str], election_timeout: float = 3.0):
        self.node_id = node_id
        self.peers = peers
        self.current_term = 0
        self.voted_for: Optional[str] = None
        self.role = NodeRole.FOLLOWER
        self.log: List[Dict] = []
        self.commit_index = -1
        self.last_applied = -1
        self.election_timeout = election_timeout
        self.last_heartbeat = time.time()
        self.votes_received = set()
        self.quorum_size = ((len(peers) + 1) // 2) + 1

    def handle_heartbeat(self, leader_id: str, term: int, commit_index: int) -> bool:
        if term >= self.current_term:
            self.current_term = term
            self.role = NodeRole.FOLLOWER
            self.voted_for = leader_id
            self.last_heartbeat = time.time()
            if commit_index > self.commit_index:
                self.commit_index = min(commit_index, len(self.log) - 1)
            return True
        return False

    def start_election(self) -> None:
        self.role = NodeRole.CANDIDATE
        self.current_term += 1
        self.voted_for = self.node_id
        self.votes_received = {self.node_id}
        self.last_heartbeat = time.time()
        logger.info(f"Node {self.node_id} initiated election for term {self.current_term}")

    def receive_vote(self, voter_id: str, term: int) -> bool:
        if self.role == NodeRole.CANDIDATE and term == self.current_term:
            self.votes_received.add(voter_id)
            if len(self.votes_received) >= self.quorum_size:
                self.role = NodeRole.LEADER
                logger.info(
                    f"Node {self.node_id} achieved quorum ({len(self.votes_received)}) and became LEADER."
                )
                return True
        return False

    def propose_entry(self, payload: Dict) -> Dict:
        if self.role != NodeRole.LEADER:
            raise RuntimeError("Only the current cluster leader can propose entries.")
        entry_idx = len(self.log)
        prev_hash = self.log[-1]["hash"] if self.log else "0" * 64
        entry_data = {
            "index": entry_idx,
            "term": self.current_term,
            "timestamp": time.time(),
            "payload": payload,
            "prev_hash": prev_hash,
        }
        raw_payload = json.dumps(entry_data, sort_keys=True).encode()
        entry_data["hash"] = hashlib.sha256(raw_payload).hexdigest()
        self.log.append(entry_data)
        return entry_data

    def commit_entries(self, peer_acks: int) -> bool:
        total_acks = peer_acks + 1
        if total_acks >= self.quorum_size:
            self.commit_index = len(self.log) - 1
            return True
        return False
