"""Extended tests for AuditChain Ledger v3.0.0 — ZK + Multi-Tenant."""
import unittest
import secrets
from backend.zkp import PedersenCommitment, RangeProofEngine, PRIME_ORDER
from backend.partition import PartitionManager, TenantPartition
from backend.crypto import CryptoEngine


class TestZKPExtended(unittest.TestCase):
    def test_commitment_different_blindings(self):
        val = 100
        r1 = secrets.randbelow(PRIME_ORDER)
        r2 = secrets.randbelow(PRIME_ORDER)
        c1 = PedersenCommitment.commit(val, r1)
        c2 = PedersenCommitment.commit(val, r2)
        self.assertNotEqual(c1, c2)
        self.assertTrue(PedersenCommitment.verify(c1, val, r1))
        self.assertTrue(PedersenCommitment.verify(c2, val, r2))

    def test_range_proof_boundary_values(self):
        engine = RangeProofEngine(bit_length=8)
        for val in [0, 1, 127, 255]:
            r = secrets.randbelow(PRIME_ORDER)
            c = PedersenCommitment.commit(val, r)
            proof = engine.generate_proof(val, r)
            self.assertTrue(engine.verify_proof(c, proof), f"Failed for val={val}")

    def test_range_proof_rejects_tampered_challenge(self):
        engine = RangeProofEngine(bit_length=8)
        val = 42
        r = secrets.randbelow(PRIME_ORDER)
        c = PedersenCommitment.commit(val, r)
        proof = engine.generate_proof(val, r)
        proof["challenge"] = (proof["challenge"] + 1) % PRIME_ORDER
        self.assertFalse(engine.verify_proof(c, proof))

    def test_out_of_range_raises(self):
        engine = RangeProofEngine(bit_length=4)
        with self.assertRaises(ValueError):
            engine.generate_proof(100, secrets.randbelow(PRIME_ORDER))

    def test_partition_key_derivation_deterministic(self):
        pm = PartitionManager(root_key=b"fixed_master_key_32bytes_long!!")
        p1 = pm.get_or_create("tenant-x")
        p2 = pm.get_or_create("tenant-x")
        self.assertEqual(p1.partition_key, p2.partition_key)

    def test_different_tenants_isolated(self):
        pm = PartitionManager(root_key=b"master_secret_key_32_bytes_seed!")
        a = pm.get_or_create("alpha")
        b = pm.get_or_create("beta")
        self.assertNotEqual(a.partition_key, b.partition_key)
        a.append_block({"msg": "hello"}, "sig-a")
        self.assertEqual(len(a.blocks), 1)
        self.assertEqual(len(b.blocks), 0)

    def test_hmac_sign_verify(self):
        key = b"test-hmac-key-32-bytes-long!!!!!"
        msg = b"important payload"
        sig = CryptoEngine.sign_hmac_sha256(key, msg)
        self.assertTrue(CryptoEngine.verify_hmac_sha256(key, msg, sig))
        self.assertFalse(CryptoEngine.verify_hmac_sha256(key, b"tampered", sig))

    def test_hash_leaf_consistency(self):
        h1 = CryptoEngine.hash_leaf("same")
        h2 = CryptoEngine.hash_leaf(b"same")
        self.assertEqual(h1, h2)


if __name__ == "__main__":
    unittest.main()
