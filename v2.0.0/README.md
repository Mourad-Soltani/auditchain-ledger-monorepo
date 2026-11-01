# AuditChain Ledger v2.0.0 — Merkle Batching Engine

High-performance batching and cryptographic proof validation with binary Merkle trees.

## Features
- Domain-separated Merkle trees (leaf / internal prefixes)
- O(log n) inclusion proofs
- Append-only JSON-L storage with cold-boot rebuild
- Batch commit + proof REST API

## Quick Start
```bash
cd v2.0.0
pip install -r requirements.txt
python -m backend.app
```

## Tests
```bash
python -m unittest tests.test_audit_chain -v
```
