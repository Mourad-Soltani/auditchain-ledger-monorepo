"""Extended tests for AuditChain Ledger v2.0.0 — Merkle Batching Engine."""
import json
import os
import tempfile
import unittest
from backend.merkle import MerkleTree
from backend.storage import LedgerStorage


class TestMerkleExtended(unittest.TestCase):
    def test_empty_tree(self):
        tree = MerkleTree([])
        self.assertIsNone(tree.root)

    def test_two_leaves(self):
        tree = MerkleTree(["a", "b"])
        self.assertIsNotNone(tree.root)
        for i, item in enumerate(["a", "b"]):
            proof = tree.get_proof(i)
            self.assertTrue(MerkleTree.verify_proof(item, proof, tree.root))

    def test_power_of_two_leaves(self):
        items = [f"leaf-{i}" for i in range(8)]
        tree = MerkleTree(items)
        for i, item in enumerate(items):
            proof = tree.get_proof(i)
            self.assertTrue(MerkleTree.verify_proof(item, proof, tree.root))

    def test_large_batch_proof(self):
        items = [f"evt-{i}" for i in range(100)]
        tree = MerkleTree(items)
        # Spot-check several indices
        for idx in [0, 49, 99]:
            proof = tree.get_proof(idx)
            self.assertTrue(MerkleTree.verify_proof(items[idx], proof, tree.root))

    def test_proof_rejects_wrong_root(self):
        tree = MerkleTree(["x", "y", "z"])
        proof = tree.get_proof(0)
        self.assertFalse(MerkleTree.verify_proof("x", proof, "0" * 64))

    def test_storage_batch_and_proof(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jsonl") as tf:
            path = tf.name
        try:
            storage = LedgerStorage(path)
            records = [{"id": i, "val": i * 10} for i in range(5)]
            indices = storage.append_batch(records)
            self.assertEqual(len(indices), 5)
            self.assertIsNotNone(storage.current_root)
            for idx in indices:
                payload = storage.get_proof_for_record(idx)
                self.assertEqual(payload["index"], idx)
                self.assertTrue(
                    MerkleTree.verify_proof(
                        json.dumps(records[idx], sort_keys=True),
                        payload["proof"],
                        payload["root"],
                    )
                )
        finally:
            if os.path.exists(path):
                os.remove(path)

    def test_cold_boot_preserves_root(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jsonl") as tf:
            path = tf.name
        try:
            s1 = LedgerStorage(path)
            s1.append_batch([{"a": 1}, {"b": 2}])
            root1 = s1.current_root
            s2 = LedgerStorage(path)
            self.assertEqual(s2.current_root, root1)
        finally:
            if os.path.exists(path):
                os.remove(path)


if __name__ == "__main__":
    unittest.main()
