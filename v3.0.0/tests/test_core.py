import unittest
import secrets
from backend.zkp import PedersenCommitment, RangeProofEngine, PRIME_ORDER
from backend.partition import PartitionManager


class TestAuditChainCore(unittest.TestCase):
    def test_pedersen_commitment(self):
        val = 42
        r = secrets.randbelow(PRIME_ORDER)
        c = PedersenCommitment.commit(val, r)
        self.assertTrue(PedersenCommitment.verify(c, val, r))
        self.assertFalse(PedersenCommitment.verify(c, val + 1, r))

    def test_zk_range_proof(self):
        engine = RangeProofEngine(bit_length=16)
        val = 1050
        r = secrets.randbelow(PRIME_ORDER)
        c = PedersenCommitment.commit(val, r)
        proof = engine.generate_proof(val, r)
        self.assertTrue(engine.verify_proof(c, proof))

    def test_tenant_isolation(self):
        pm = PartitionManager(root_key=b"master_secret_key_32_bytes_seed!")
        p1 = pm.get_or_create("tenant-alpha")
        p2 = pm.get_or_create("tenant-beta")
        self.assertNotEqual(p1.partition_key, p2.partition_key)


if __name__ == "__main__":
    unittest.main()
