# AuditChain Ledger — Test Suite & Proofs Summary

**Total automated unit tests: 62** (all passing under Python 3.11 / 3.12)

## Coverage by Version

| Version | Test Files | Test Count | Focus Areas |
|---------|------------|------------|-------------|
| v1.0.0 | test_ledger.py, test_api.py, test_ledger_extended.py | 13 | Genesis, append, hash continuity, tamper detection, persistence, API |
| v2.0.0 | test_audit_chain.py, test_merkle_extended.py | 11 | Tree construction, odd-leaf padding, proofs, cold-boot, batch storage |
| v3.0.0 | test_core.py, test_zkp_extended.py | 11 | Pedersen commitments, range proofs, tenant isolation, HMAC |
| v4.0.0 | test_distributed.py, test_distributed_extended.py | 13 | Raft election/commit, sharding distribution, healing, PKI |
| v5.0.0 | test_audit_chain.py, test_pqc_extended.py | 14 | Lattice sign/verify, Shamir k-of-n, AI compliance, inter-partition |

## Property Categories Proven

1. **Hash-chain integrity** — any bit flip or reordering is detected.
2. **Merkle inclusion** — proofs verify correctly; tampered leaves are rejected.
3. **Zero-knowledge range** — valid proofs accept; altered challenges reject.
4. **Tenant isolation** — partition keys differ; blocks do not leak across tenants.
5. **Consensus quorum** — leader election and commit require majority.
6. **Threshold reconstruction** — any qualified subset of shares recovers the secret.
7. **PQC binding** — signatures verify for the original message and fail for tampered messages.
8. **Compliance scoring** — sanctioned entities and statistical outliers are blocked.

## How to Run

```bash
# From monorepo root
for v in v1.0.0 v2.0.0 v3.0.0 v4.0.0 v5.0.0; do
  (cd $v && PYTHONPATH=. python -m pytest tests/ -q)
done

# Or via CI
# .github/workflows/ci.yml runs the full matrix
```

## Performance Micro-benchmarks

See `benchmarks/run_benchmarks.py`. Typical results on a modern CPU:

- v1 append 100 events + verify: low tens of ms
- v2 Merkle build 1 000 leaves: single-digit to low tens of ms
- v5 educational PQC sign/verify: low single-digit ms (N=64 parameters)

These numbers demonstrate practical pure-Python performance for the reference implementations; production deployments should use optimized libraries for lattice cryptography.
