import json
import tempfile
from backend.ledger import AuditLedger, Block


def test_ledger_genesis_creation():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=True) as tmp:
        ledger = AuditLedger(storage_path=tmp.name)
        assert len(ledger.chain) == 1
        assert ledger.chain[0].index == 0
        assert ledger.chain[0].event_type == "GENESIS"
        is_valid, err = ledger.verify_integrity()
        assert is_valid is True
        assert err is None


def test_append_and_integrity_verification():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=True) as tmp:
        ledger = AuditLedger(storage_path=tmp.name)
        b1 = ledger.append_event("USER_LOGIN", "alice", {"ip": "192.168.1.10"})
        b2 = ledger.append_event("DOCUMENT_DELETE", "bob", {"doc_id": "doc-99"})
        assert len(ledger.chain) == 3
        assert b1.prev_hash == ledger.chain[0].hash
        assert b2.prev_hash == b1.hash
        is_valid, _ = ledger.verify_integrity()
        assert is_valid is True


def test_tamper_detection():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=True) as tmp:
        ledger = AuditLedger(storage_path=tmp.name)
        ledger.append_event("TX_TRANSFER", "alice", {"amount": 50})
        ledger.chain[1].data["amount"] = 50000
        is_valid, error = ledger.verify_integrity()
        assert is_valid is False
        assert "Tampered payload detected" in error
