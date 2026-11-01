# AuditChain Ledger v1.0.0 — Foundation Engine

Immutable, zero-dependency (beyond Flask for the API), append-only SHA-256 audit logging system.

## Features
- Cryptographically linked hash chain
- Genesis block + integrity verification
- Flask REST API (`/api/events`, `/api/chain`, `/api/verify`)
- Thread-safe append + JSON persistence

## Quick Start
```bash
cd v1.0.0
pip install -r requirements.txt
python -m backend.app
```

## Tests
```bash
pytest tests/ -v
```
