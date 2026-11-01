# AuditChain Ledger Monorepo

**Sovereign, progressive cryptographic audit ledger platform**  
Versions **v1.0.0 → v5.0.0** in a single unified repository.

## Release Manifest

| Version | Codename | Focus |
|---------|----------|-------|
| **v1.0.0** | Foundation Engine | Immutable SHA-256 hash-chained append-only ledger + Flask API |
| **v2.0.0** | Merkle Batching Engine | Binary Merkle trees, inclusion proofs, JSON-L persistence |
| **v3.0.0** | Enterprise Multi-Tenant | Zero-Knowledge Range Proofs, tenant isolation, HMAC signatures |
| **v4.0.0** | Autonomous Distributed | Raft consensus, consistent-hash sharding, auto-healing |
| **v5.0.0** | Sovereign Post-Quantum | Lattice-based Dilithium-style PQC, Shamir VSS, AI compliance |

Each version is a **self-contained Python package** with its own `backend/`, `tests/`, and `requirements.txt`.

## Quick Start (any version)

```bash
cd vX.Y.Z
pip install -r requirements.txt
# Run tests
python -m unittest discover -s tests -v
# Or (v1/v2) start the API
python -m backend.app
```

## Repository Structure

```
auditchain-ledger-monorepo/
├── v1.0.0/
│   ├── backend/          # ledger.py, app.py, config.py
│   ├── tests/
│   ├── requirements.txt
│   └── README.md
├── v2.0.0/
│   ├── backend/          # merkle.py, storage.py, app.py
│   ├── tests/
│   └── ...
├── v3.0.0/
│   ├── backend/          # zkp.py, partition.py, crypto.py
│   └── ...
├── v4.0.0/
│   ├── backend/          # consensus.py, sharding.py, healing.py, pki.py
│   └── ...
├── v5.0.0/
│   ├── backend/          # pqc.py, secret_sharing.py, ai_compliance.py, interop.py
│   └── ...
├── .github/workflows/
│   └── ci.yml            # Multi-version test matrix
└── README.md             # This file
```

## Design Principles

- **Pure Python** core (stdlib + minimal Flask for APIs)
- **Zero external cryptographic dependencies**
- Progressive capability growth while remaining independently runnable
- Deterministic tests suitable for CI

## License & Ownership

All intellectual property belongs to **Mourad Soltani**.  
This monorepo is prepared for acquisition / integration purposes.

---

*AuditChain Ledger — Built for zero-trust, post-quantum, and regulatory-grade audit trails.*
