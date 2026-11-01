"""Extended tests for AuditChain Ledger v1.0.0 — Foundation Engine."""
import json
import tempfile
import os
from backend.ledger import AuditLedger, Block
from backend.config import GENESIS_PREV_HASH


def test_multiple_append_sequence():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=True) as tmp:
        ledger = AuditLedger(storage_path=tmp.name)
        for i in range(10):
            ledger.append_event(f"EVENT_{i}", f"actor_{i}", {"seq": i})
        assert len(ledger.chain) == 11  # genesis + 10
        ok, err = ledger.verify_integrity()
        assert ok is True
        assert err is None


def test_hash_chain_continuity():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=True) as tmp:
        ledger = AuditLedger(storage_path=tmp.name)
        b1 = ledger.append_event("A", "u1", {"x": 1})
        b2 = ledger.append_event("B", "u2", {"x": 2})
        b3 = ledger.append_event("C", "u3", {"x": 3})
        assert b1.prev_hash == ledger.chain[0].hash
        assert b2.prev_hash == b1.hash
        assert b3.prev_hash == b2.hash


def test_persist_and_reload():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        path = tmp.name
    try:
        ledger = AuditLedger(storage_path=path)
        ledger.append_event("PERSIST", "admin", {"k": "v"})
        length = len(ledger.chain)
        del ledger
        reloaded = AuditLedger(storage_path=path)
        assert len(reloaded.chain) == length
        ok, _ = reloaded.verify_integrity()
        assert ok is True
    finally:
        if os.path.exists(path):
            os.remove(path)


def test_tamper_prev_hash_detection():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=True) as tmp:
        ledger = AuditLedger(storage_path=tmp.name)
        ledger.append_event("TX", "alice", {"amount": 10})
        ledger.chain[1].prev_hash = "0" * 64
        ok, error = ledger.verify_integrity()
        assert ok is False
        assert error is not None


def test_tamper_index_detection():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=True) as tmp:
        ledger = AuditLedger(storage_path=tmp.name)
        ledger.append_event("TX", "alice", {"amount": 10})
        ledger.chain[1].index = 99
        ok, error = ledger.verify_integrity()
        assert ok is False


def test_block_payload_canonical():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=True) as tmp:
        ledger = AuditLedger(storage_path=tmp.name)
        block = ledger.append_event("CANON", "sys", {"b": 2, "a": 1})
        # Hash must be deterministic regardless of dict insertion order
        recalculated = block.calculate_hash()
        assert block.hash == recalculated


def test_genesis_immutable_fields():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=True) as tmp:
        ledger = AuditLedger(storage_path=tmp.name)
        g = ledger.chain[0]
        assert g.index == 0
        assert g.prev_hash == GENESIS_PREV_HASH
        assert g.event_type == "GENESIS"
