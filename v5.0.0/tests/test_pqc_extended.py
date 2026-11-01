"""Extended tests for AuditChain Ledger v5.0.0 — Sovereign PQC Platform."""
import unittest
from backend.pqc import PQCDilithiumSigner, PolyRing, N, Q
from backend.secret_sharing import ThresholdSecretSharer, FIELD_PRIME
from backend.ai_compliance import ComplianceAnomalyEngine
from backend.interop import PartitionBridgeRouter, MerkleStateTree, sha256d


class TestPQCExtended(unittest.TestCase):
    def test_poly_add_mul_identity(self):
        a = PolyRing([1, 2, 3] + [0] * (N - 3))
        b = PolyRing([4, 5, 6] + [0] * (N - 3))
        s = a + b
        self.assertEqual(s.coeffs[0], 5)
        self.assertEqual(s.coeffs[1], 7)

    def test_sign_verify_multiple_messages(self):
        signer = PQCDilithiumSigner()
        pk = signer.get_public_key()
        for msg in [b"msg1", b"msg2", b"another longer message"]:
            sig = signer.sign(msg)
            self.assertTrue(PQCDilithiumSigner.verify(pk, msg, sig))
            self.assertFalse(PQCDilithiumSigner.verify(pk, msg + b"x", sig))

    def test_different_signers_independent(self):
        s1 = PQCDilithiumSigner()
        s2 = PQCDilithiumSigner()
        self.assertNotEqual(s1.get_public_key()[0], s2.get_public_key()[0])

    def test_secret_sharing_k_of_n(self):
        sharer = ThresholdSecretSharer(threshold=2, total_shares=4)
        secret = 12345678901234567890
        shares = sharer.split_secret(secret)
        self.assertEqual(len(shares), 4)
        # Any 2 shares should reconstruct
        self.assertEqual(sharer.reconstruct_secret(shares[:2]), secret)
        self.assertEqual(sharer.reconstruct_secret(shares[1:3]), secret)
        self.assertEqual(sharer.reconstruct_secret([shares[0], shares[3]]), secret)

    def test_secret_sharing_rejects_insufficient(self):
        with self.assertRaises(ValueError):
            ThresholdSecretSharer.reconstruct_secret([(1, 10)])

    def test_ai_compliance_updates_stats(self):
        engine = ComplianceAnomalyEngine(risk_threshold=0.9)
        engine.evaluate_transaction({"sender": "a", "recipient": "b", "amount": 5000})
        engine.evaluate_transaction({"sender": "a", "recipient": "b", "amount": 5100})
        self.assertNotEqual(engine.mean_amount, 5000.0)

    def test_ai_compliance_outlier(self):
        engine = ComplianceAnomalyEngine(risk_threshold=0.5)
        # Feed normal data first
        for _ in range(20):
            engine.evaluate_transaction({"sender": "a", "recipient": "b", "amount": 5000.0})
        approved, score, reason = engine.evaluate_transaction(
            {"sender": "a", "recipient": "b", "amount": 5_000_000.0}
        )
        self.assertFalse(approved)
        self.assertIn("OUTLIER", reason)

    def test_interop_idempotent_mint(self):
        a = PartitionBridgeRouter("PART_A")
        b = PartitionBridgeRouter("PART_B")
        payload = b"transfer-100"
        receipt = a.generate_transfer_receipt("PART_B", payload)
        tree = MerkleStateTree([payload])
        self.assertTrue(b.apply_remote_receipt(receipt, tree.root.hex()))
        self.assertFalse(b.apply_remote_receipt(receipt, tree.root.hex()))

    def test_merkle_state_tree_single_leaf(self):
        leaf = b"only"
        tree = MerkleStateTree([leaf])
        self.assertEqual(tree.root, sha256d(leaf))

    def test_merkle_state_tree_empty(self):
        tree = MerkleStateTree([])
        self.assertEqual(len(tree.root), 32)


if __name__ == "__main__":
    unittest.main()
