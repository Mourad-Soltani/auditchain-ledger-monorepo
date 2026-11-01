"""Extended tests for AuditChain Ledger v4.0.0 — Distributed Engine."""
import unittest
from backend.consensus import RaftConsensusEngine, NodeRole
from backend.sharding import ConsistentHashRing
from backend.healing import AutoHealingEngine
from backend.pki import NodeKeyAuthority


class TestDistributedExtended(unittest.TestCase):
    def test_raft_follower_accepts_higher_term_heartbeat(self):
        engine = RaftConsensusEngine("n1", peers=["n2", "n3"])
        engine.current_term = 1
        accepted = engine.handle_heartbeat("n2", term=2, commit_index=0)
        self.assertTrue(accepted)
        self.assertEqual(engine.role, NodeRole.FOLLOWER)
        self.assertEqual(engine.current_term, 2)

    def test_raft_reject_stale_heartbeat(self):
        engine = RaftConsensusEngine("n1", peers=["n2", "n3"])
        engine.current_term = 5
        accepted = engine.handle_heartbeat("n2", term=3, commit_index=0)
        self.assertFalse(accepted)

    def test_raft_only_leader_proposes(self):
        engine = RaftConsensusEngine("n1", peers=["n2", "n3"])
        with self.assertRaises(RuntimeError):
            engine.propose_entry({"x": 1})

    def test_raft_quorum_commit(self):
        engine = RaftConsensusEngine("n1", peers=["n2", "n3", "n4"])
        engine.start_election()
        engine.receive_vote("n2", engine.current_term)
        engine.receive_vote("n3", engine.current_term)
        self.assertEqual(engine.role, NodeRole.LEADER)
        engine.propose_entry({"action": "write"})
        self.assertTrue(engine.commit_entries(peer_acks=2))

    def test_sharding_uniform_distribution(self):
        ring = ConsistentHashRing(replicas=64)
        for node in ["A", "B", "C", "D"]:
            ring.add_node(node)
        counts = {"A": 0, "B": 0, "C": 0, "D": 0}
        for i in range(1000):
            n = ring.get_node(f"key-{i}")
            counts[n] += 1
        # Each node should get a reasonable share
        for c in counts.values():
            self.assertGreater(c, 100)
            self.assertLess(c, 400)

    def test_sharding_remove_redistributes(self):
        ring = ConsistentHashRing(replicas=32)
        ring.add_node("X")
        ring.add_node("Y")
        before = ring.get_node("stable-key")
        ring.remove_node("X")
        after = ring.get_node("stable-key")
        self.assertEqual(after, "Y")

    def test_healing_detects_prev_hash_break(self):
        healer = AutoHealingEngine()
        b0 = {"index": 0, "prev_hash": "0" * 64, "data": {"v": 1}}
        b0["hash"] = healer.compute_block_hash(b0)
        b1 = {"index": 1, "prev_hash": "deadbeef" * 8, "data": {"v": 2}}
        b1["hash"] = healer.compute_block_hash(b1)
        corrupted = healer.audit_chain_integrity([b0, b1])
        self.assertIn(1, corrupted)

    def test_healing_clean_chain(self):
        healer = AutoHealingEngine()
        chain = []
        prev = "0" * 64
        for i in range(5):
            block = {"index": i, "prev_hash": prev, "data": {"i": i}}
            block["hash"] = healer.compute_block_hash(block)
            chain.append(block)
            prev = block["hash"]
        self.assertEqual(healer.audit_chain_integrity(chain), [])

    def test_pki_unique_keys(self):
        a1 = NodeKeyAuthority()
        a2 = NodeKeyAuthority()
        self.assertNotEqual(a1.public_key, a2.public_key)


if __name__ == "__main__":
    unittest.main()
