# Architecture — AuditChain Ledger Monorepo

## Design Philosophy

AuditChain is a **progressive** cryptographic audit platform. Each version builds on the previous while remaining independently runnable. The monorepo deliberately keeps every release self-contained so acquirers can adopt the maturity level that matches their risk appetite.

## Version Progression

```
v1.0.0  Foundation Engine
   │    SHA-256 hash-chained append-only ledger + Flask REST API
   │
v2.0.0  Merkle Batching Engine
   │    Binary Merkle trees, O(log n) inclusion proofs, JSON-L persistence
   │
v3.0.0  Enterprise Multi-Tenant
   │    Pedersen ZK range proofs, tenant isolation, HMAC non-repudiation
   │
v4.0.0  Autonomous Distributed
   │    Raft-style quorum, consistent-hash sharding, auto-healing
   │
v5.0.0  Sovereign Post-Quantum
        Educational lattice signatures, Shamir VSS, AI compliance, inter-partition bridge
```

## Core Invariants Across Versions

1. **Append-only** — historical records are never mutated in place.
2. **Cryptographic binding** — every entry references a prior hash or tree root.
3. **Deterministic verification** — given the same inputs, verification always yields the same result.
4. **Minimal external crypto dependencies** — core algorithms use only the Python standard library (hashlib, secrets, etc.). Flask is used solely for optional HTTP surfaces.

## Module Map

| Version | Primary modules | Responsibility |
|---------|-----------------|----------------|
| v1 | `ledger.py`, `app.py`, `config.py` | Block structure, hash chain, REST API |
| v2 | `merkle.py`, `storage.py`, `app.py` | Tree construction, proofs, append-only store |
| v3 | `zkp.py`, `partition.py`, `crypto.py` | Range proofs, tenant isolation, HMAC |
| v4 | `consensus.py`, `sharding.py`, `healing.py`, `pki.py` | Quorum, key placement, integrity repair |
| v5 | `pqc.py`, `secret_sharing.py`, `ai_compliance.py`, `interop.py` | Lattice demo, threshold secrets, risk scoring, cross-partition receipts |

## Testing Strategy

- Each version ships its own `tests/` package.
- Current monorepo contains **60+ unit tests** covering core cryptographic and structural properties.
- CI runs the full matrix on Python 3.11 and 3.12.

## Deployment Notes

- All versions are pure Python and can run in air-gapped environments.
- v1 and v2 expose optional Flask APIs; the cryptographic cores have no network requirement.
- See `SECURITY.md` for the explicit threat model and production hardening recommendations.

## Future Extension Points

- Replace educational lattice code with NIST-standardized implementations.
- Add formal verifiable secret sharing (Feldman / Pedersen commitments).
- Introduce authenticated peer transport for the Raft module.
- Export Merkle roots and receipts to external anchoring services.
