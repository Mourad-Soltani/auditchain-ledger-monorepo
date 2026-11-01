import unittest
from backend.pqc import PQCDilithiumSigner
from backend.secret_sharing import ThresholdSecretSharer
from backend.ai_compliance import ComplianceAnomalyEngine
from backend.interop import PartitionBridgeRouter, MerkleStateTree


class TestAuditChainLedger(unittest.TestCase):
    def test_lattice_signature_lifecycle(self):
        signer = PQCDilithiumSigner()
        pk = signer.get_public_key()
        msg = b"AuditChain Ledger Transaction Block #50012"
        sig = signer.sign(msg)
        self.assertTrue(PQCDilithiumSigner.verify(pk, msg, sig))
        tampered_msg = b"Tampered Transaction Content"
        self.assertFalse(PQCDilithiumSigner.verify(pk, tampered_msg, sig))

    def test_threshold_secret_reconstruction(self):
        sharer = ThresholdSecretSharer(threshold=3, total_shares=5)
        master_secret = 0xDEADBEEFCAFE1234567890ABCDEF1234567890ABCDEF
        shares = sharer.split_secret(master_secret)
        self.assertEqual(len(shares), 5)
        reconstructed = sharer.reconstruct_secret(shares[:3])
        self.assertEqual(reconstructed, master_secret)
        reconstructed_other_subset = sharer.reconstruct_secret([shares[0], shares[2], shares[4]])
        self.assertEqual(reconstructed_other_subset, master_secret)

    def test_ai_compliance_engine(self):
        engine = ComplianceAnomalyEngine(risk_threshold=0.80)
        approved, score, status = engine.evaluate_transaction(
            {"sender": "alice", "recipient": "bob", "amount": 5200.0}
        )
        self.assertTrue(approved)
        self.assertEqual(status, "APPROVED")
        approved_sanc, score_sanc, reason = engine.evaluate_transaction(
            {"sender": "SANCTIONED_NODE_01", "recipient": "bob", "amount": 10.0}
        )
        self.assertFalse(approved_sanc)
        self.assertEqual(reason, "SANCTIONED_ENTITY_MATCH")

    def test_cross_partition_bridge(self):
        router_a = PartitionBridgeRouter("PARTITION_FINANCE")
        router_b = PartitionBridgeRouter("PARTITION_SUPPLY_CHAIN")
        payload = b"Cross-ledger transfer credit: 1500 tokens"
        receipt = router_a.generate_transfer_receipt("PARTITION_SUPPLY_CHAIN", payload)
        tree = MerkleStateTree([payload])
        applied = router_b.apply_remote_receipt(receipt, tree.root.hex())
        self.assertTrue(applied)
        self.assertFalse(router_b.apply_remote_receipt(receipt, tree.root.hex()))


if __name__ == "__main__":
    unittest.main()
