# AuditChain Ledger Monorepo

**Progressive pure-Python cryptographic audit platform**  
Versions **v1.0.0 → v5.0.0** in a single unified repository.

## Release Manifest

| Version | Codename | Focus | Maturity |
|---------|----------|-------|----------|
| **v1.0.0** | Foundation Engine | SHA-256 hash chain + Flask API | Production-usable core |
| **v2.0.0** | Merkle Batching | Binary Merkle trees, inclusion proofs, JSON-L | Production-usable core |
| **v3.0.0** | Enterprise Multi-Tenant | Educational ZK range proofs, tenant isolation | Reference / educational |
| **v4.0.0** | Autonomous Distributed | Raft-style quorum, sharding, auto-healing | Reference / educational |
| **v5.0.0** | Sovereign Post-Quantum | Educational lattice signatures, Shamir VSS, AI compliance | Reference / educational |

## Quick Start

```bash
cd vX.Y.Z
pip install -e ".[test]"          # or pip install -r requirements.txt
PYTHONPATH=. python -m pytest tests/ -q
```

## Repository Layout

```
auditchain-ledger-monorepo/
├── v1.0.0/ … v5.0.0/     # Independent, self-contained packages
├── benchmarks/            # Micro-benchmarks
├── docs/                  # Test-suite summary, revised acquisition proposal
├── ARCHITECTURE.md        # Design progression
├── SECURITY.md            # Threat model & explicit limitations
├── .github/workflows/     # CI matrix
└── README.md
```

## Test Suite

**62 automated unit tests** covering integrity, proofs, isolation, consensus, threshold sharing and educational PQC.  
See `docs/TEST_SUITE_AND_PROOFS.md`.

## Security Notice

All advanced cryptographic modules (especially v3 ZK and v5 lattice) are **educational reference implementations**.  
They are **not** production-ready NIST-validated cryptography.  
Read `SECURITY.md` before any deployment consideration.

## Documentation

- [Architecture](ARCHITECTURE.md)
- [Security & Threat Model](SECURITY.md)
- [Test Suite & Proofs](docs/TEST_SUITE_AND_PROOFS.md)
- [Revised Acquisition Proposal](docs/Acquisition_Proposal_Revised.md)

## License & Ownership

All intellectual property belongs to **Mourad Soltani**.

---

*AuditChain Ledger — Built for zero-trust, educational post-quantum exploration, and regulatory-grade audit trail research.*
