#!/usr/bin/env python3
"""
Deterministic micro-benchmarks for AuditChain Ledger cores.
Run from monorepo root:  python benchmarks/run_benchmarks.py
"""
import time
import sys
import os
import json
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def bench(name, fn, rounds=5):
    times = []
    for _ in range(rounds):
        t0 = time.perf_counter()
        fn()
        times.append((time.perf_counter() - t0) * 1000)
    avg = sum(times) / len(times)
    print(f"  {name:<45} {avg:8.3f} ms  (avg of {rounds})")
    return avg


def bench_v1():
    sys.path.insert(0, os.path.join(ROOT, "v1.0.0"))
    from backend.ledger import AuditLedger
    with tempfile.NamedTemporaryFile(suffix=".json") as tmp:
        ledger = AuditLedger(storage_path=tmp.name)
        def append_100():
            for i in range(100):
                ledger.append_event("BENCH", "bench", {"i": i})
        bench("v1 append 100 events", append_100)
        bench("v1 verify_integrity", lambda: ledger.verify_integrity())


def bench_v2():
    sys.path.insert(0, os.path.join(ROOT, "v2.0.0"))
    from backend.merkle import MerkleTree
    items = [json.dumps({"id": i}) for i in range(1000)]
    def build():
        MerkleTree(items)
    tree = MerkleTree(items)
    bench("v2 Merkle build 1000 leaves", build)
    bench("v2 get_proof(mid)", lambda: tree.get_proof(500))
    proof = tree.get_proof(500)
    bench("v2 verify_proof", lambda: MerkleTree.verify_proof(items[500], proof, tree.root))


def bench_v5():
    sys.path.insert(0, os.path.join(ROOT, "v5.0.0"))
    from backend.pqc import PQCDilithiumSigner
    from backend.secret_sharing import ThresholdSecretSharer
    signer = PQCDilithiumSigner()
    pk = signer.get_public_key()
    msg = b"benchmark message"
    bench("v5 PQC keygen", lambda: PQCDilithiumSigner())
    bench("v5 PQC sign", lambda: signer.sign(msg))
    sig = signer.sign(msg)
    bench("v5 PQC verify", lambda: PQCDilithiumSigner.verify(pk, msg, sig))
    sharer = ThresholdSecretSharer(3, 5)
    secret = 0xDEADBEEF
    shares = sharer.split_secret(secret)
    bench("v5 Shamir split 3-of-5", lambda: sharer.split_secret(secret))
    bench("v5 Shamir reconstruct", lambda: sharer.reconstruct_secret(shares[:3]))


if __name__ == "__main__":
    print("AuditChain Ledger — Micro-benchmarks\n")
    print("v1 Foundation")
    bench_v1()
    print("\nv2 Merkle")
    bench_v2()
    print("\nv5 Sovereign")
    bench_v5()
    print("\nDone.")
