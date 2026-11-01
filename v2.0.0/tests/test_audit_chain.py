import unittest
import os
import json
import tempfile
from backend.merkle import MerkleTree
from backend.storage import LedgerStorage


class TestAuditChain(unittest.TestCase):
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jsonl")
        self.temp_file.close()
        self.storage = LedgerStorage(self.temp_file.name)

    def tearDown(self):
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)

    def test_single_leaf_root(self):
        tree = MerkleTree(["entry-0"])
        self.assertEqual(tree.root, tree.hash_leaf("entry-0"))

    def test_odd_leaves_proof_verification(self):
        items = ["log-A", "log-B", "log-C"]
        tree = MerkleTree(items)
        self.assertIsNotNone(tree.root)
        for i, item in enumerate(items):
            proof = tree.get_proof(i)
            self.assertTrue(MerkleTree.verify_proof(item, proof, tree.root))

    def test_tampered_proof_rejection(self):
        items = ["tx1", "tx2", "tx3", "tx4"]
        tree = MerkleTree(items)
        proof = tree.get_proof(1)
        self.assertFalse(MerkleTree.verify_proof("tx1_tampered", proof, tree.root))

    def test_persistence_and_cold_boot(self):
        records = [{"action": "login", "uid": 1}, {"action": "deposit", "amount": 100}]
        self.storage.append_batch(records)
        root_pre = self.storage.current_root

        boot_storage = LedgerStorage(self.temp_file.name)
        self.assertEqual(boot_storage.current_root, root_pre)
        proof_data = boot_storage.get_proof_for_record(0)
        self.assertTrue(
            MerkleTree.verify_proof(
                json.dumps(records[0], sort_keys=True),
                proof_data["proof"],
                root_pre
            )
        )


if __name__ == "__main__":
    unittest.main()
