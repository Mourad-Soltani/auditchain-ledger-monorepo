import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
LEDGER_STORAGE_PATH = os.getenv("LEDGER_STORAGE_PATH", str(BASE_DIR / "data" / "ledger.json"))
GENESIS_PREV_HASH = "0" * 64
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 5000))
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
