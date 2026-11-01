from flask import Flask, request, jsonify
from backend.storage import LedgerStorage
from backend.merkle import MerkleTree
import json

app = Flask(__name__)
storage = LedgerStorage("audit_chain_live.jsonl")


@app.route("/api/batch", methods=["POST"])
def append_batch():
    data = request.get_json()
    if not data or "records" not in data or not isinstance(data["records"], list):
        return jsonify({"error": "Invalid payload format. Expected list in 'records'."}), 400
    indices = storage.append_batch(data["records"])
    return jsonify({
        "status": "committed",
        "indices": indices,
        "merkle_root": storage.current_root
    }), 201


@app.route("/api/proof", methods=["GET"])
def get_proof():
    index_arg = request.args.get("index")
    if index_arg is None or not index_arg.isdigit():
        return jsonify({"error": "Query parameter 'index' is required and must be an integer."}), 400
    try:
        proof_payload = storage.get_proof_for_record(int(index_arg))
        return jsonify(proof_payload), 200
    except IndexError as e:
        return jsonify({"error": str(e)}), 404


@app.route("/api/verify", methods=["POST"])
def verify_proof():
    data = request.get_json()
    required_keys = {"record", "proof", "root"}
    if not data or not required_keys.issubset(data.keys()):
        return jsonify({"error": "Missing required fields: record, proof, root"}), 400
    serialized = json.dumps(data["record"], sort_keys=True)
    valid = MerkleTree.verify_proof(serialized, data["proof"], data["root"])
    return jsonify({"valid": valid, "root": data["root"]}), 200


if __name__ == "__main__":
    app.run(port=8080, debug=False)
