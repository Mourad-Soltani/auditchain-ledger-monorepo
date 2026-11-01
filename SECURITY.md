# Security Policy & Threat Model — AuditChain Ledger

## Scope

This document covers the AuditChain Ledger monorepo (v1.0.0 – v5.0.0).  
All cryptographic modules are **educational / reference implementations** intended for research, prototyping, and acceleration of internal R&D. They are **not** production-ready NIST-validated cryptography.

## Security Goals

| Goal | Description |
|------|-------------|
| Tamper evidence | Any modification of historical ledger entries is detectable via hash-chain or Merkle proofs |
| Integrity | Cryptographic binding of records to predecessors / tree roots |
| Isolation | Multi-tenant partitions use derived keys; cross-tenant leakage is out of scope of the core ledger |
| Threshold secrecy | Shamir sharing protects a secret until *k* shares are combined |
| Post-quantum readiness (educational) | Lattice-based signatures demonstrate structure for future migration |

## Explicit Non-Goals / Known Limitations

1. **v5 Lattice signatures** use reduced parameters (N=64) and simplified Fiat-Shamir for practical pure-Python runtime. They do **not** claim the security level of NIST ML-DSA / Dilithium.
2. **v3 ZK Range Proofs** are pedagogical Pedersen + bit-decomposition proofs, not production Bulletproofs or Plonk.
3. **v4 Raft** is a simplified quorum engine for demonstration; it lacks full network transport, log compaction, and membership change protocols.
4. No formal side-channel resistance (timing, cache, etc.).
5. No hardware root of trust or HSM integration in the reference code.
6. Secret sharing assumes an honest majority for reconstruction and does not include Feldman/Pedersen verifiable share proofs in the base implementation.

## Threat Model (High Level)

**Adversaries considered**
- External attacker with read/write access to storage who attempts to alter historical records.
- Malicious tenant attempting to forge proofs for another tenant’s partition.
- Network adversary (for distributed modules) attempting to disrupt consensus or inject invalid blocks.

**Adversaries not fully mitigated in reference code**
- Nation-state quantum adversary against classical hash/signature assumptions in v1–v4.
- Side-channel attacks against pure-Python implementations.
- Supply-chain compromise of the host Python runtime.

## Recommended Production Hardening

Before any production or regulated deployment:

1. Replace educational lattice code with a reviewed library implementing NIST ML-DSA / ML-KEM (or equivalent).
2. Commission an independent cryptographic review of the specific modules you intend to use.
3. Add authenticated encryption for data at rest and TLS for any network surface.
4. Introduce formal key management (HSM / KMS) and secure key lifecycle.
5. Expand fuzzing and property-based testing beyond the unit suite.
6. Obtain necessary compliance certifications for the target jurisdiction (SOC 2, ISO 27001, etc.).

## Reporting Security Issues

Please report suspected vulnerabilities privately to the repository owner.  
Do not open public issues for security-sensitive findings until a fix or mitigation is available.

## Version History

- 2026-11-01: Initial threat model published with monorepo release.
