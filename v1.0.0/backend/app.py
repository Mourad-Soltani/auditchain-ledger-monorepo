from flask import Flask, jsonify, request
from backend.config import DEBUG, HOST, PORT
from backend.ledger import AuditLedger

app = Flask(__name__)
ledger = AuditLedger()


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "service": "AuditChain Ledger", "version": "1.0.0"}), 200


@app.route("/api/events", methods=["POST"])
def append_event():
    payload = request.get_json(silent=True) or {}
    event_type = payload.get("event_type")
    actor = payload.get("actor")
    data = payload.get("data")
    if not event_type or not actor or data is None or not isinstance(data, dict):
        return jsonify({"error": "Fields 'event_type', 'actor', and object 'data' are required."}), 400
    block = ledger.append_event(event_type=event_type, actor=actor, data=data)
    return jsonify({"message": "Event recorded", "block": block.to_dict()}), 201


@app.route("/api/chain", methods=["GET"])
def get_chain():
    return jsonify({"length": len(ledger.chain), "chain": [b.to_dict() for b in ledger.chain]}), 200


@app.route("/api/verify", methods=["GET"])
def verify_chain():
    is_valid, error = ledger.verify_integrity()
    return jsonify({"valid": is_valid, "error": error}), 200 if is_valid else 409


if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=DEBUG)
