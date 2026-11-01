# AuditChain Ledger v4.0.0 — Autonomous Distributed Engine

Fault-tolerant consensus, dynamic sharding, and anti-tamper auto-healing.

## Features
- Raft-style quorum consensus (leader election + log proposal)
- Consistent-hash ring sharding
- Auto-healing integrity scanner
- Node key authority (HMAC-based demo PKI)

## Tests
```bash
cd v4.0.0
python -m unittest tests.test_distributed -v
```
