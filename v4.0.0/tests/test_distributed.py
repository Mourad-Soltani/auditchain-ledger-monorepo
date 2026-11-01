import unittest
from backend.consensus import RaftConsensusEngine, NodeRole
from backend.sharding import ConsistentHashRing
from backend.healing import AutoHealingEngine
from backend.pki import NodeKeyAuthority


class TestDistributedModules(unittest.TestCase):
    def test_raft_election_and_proposal(self):
        engine = RaftConsensusEngine("node-1", peers=["node-2", "node-3", "node-4"])
        engine.start_election()
        self.assertEqual(engine.role, NodeRole.CANDIDATE)
        engine.receive_vote("node-2", engine.current_term)
        engine.receive_vote("node-3", engine.current_term)
        self.assertEqual(engine.role, NodeRole.LEADER)
        entry = engine.propose_entry({"action": "transfer", "amount": 100})
        self.assertIn("hash", entry)
        self.assertTrue(engine.commit_entries(peer_acks=2))

    def test_consistent_hash_ring(self):
        ring = ConsistentHashRing(replicas=32)
        ring.add_node("shard-A")
        ring.add_node("shard-B")
        ring.add_node("shard-C")
        node = ring.get_node("user:42")
        self.assertIn(node, {"shard-A", "shard-B", "shard-C"})
        ring.remove_node("shard-B")
        self.assertNotIn("shard-B", ring.physical_nodes)

    def test_healing_detection(self):
        healer = AutoHealingEngine()
        good_block = {"index": 0, "prev_hash": "0" * 64, "data": {"v": 1}}
        good_block["hash"] = healer.compute_block_hash(good_block)
        chain = [good_block]
        # Tamper
        bad = dict(good_block)
        bad["data"] = {"v": 999}
        chain.append(bad)
        corrupted = healer.audit_chain_integrity(chain)
        self.assertTrue(len(corrupted) > 0)

    def test_pki_sign(self):
        auth = NodeKeyAuthority()
        sig = auth.sign_transaction(b"payload-data")
        self.assertTrue(NodeKeyAuthority.verify_signature(auth.public_key, b"payload-data", sig))


if __name__ == "__main__":
    unittest.main()
