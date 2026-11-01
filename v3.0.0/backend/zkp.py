import hashlib
import secrets
from typing import Dict, List, Any

# Finite field prime order for ZKRP demo (secp256k1 order)
PRIME_ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
GENERATOR_G = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
GENERATOR_H = 0x25B563BE27F6F101F00B5E351C43B22EAE435E339A0F0430842A749359679E13


class PedersenCommitment:
    @staticmethod
    def commit(val: int, blinding: int) -> int:
        return (val * GENERATOR_G + blinding * GENERATOR_H) % PRIME_ORDER

    @staticmethod
    def verify(commitment: int, val: int, blinding: int) -> bool:
        expected = (val * GENERATOR_G + blinding * GENERATOR_H) % PRIME_ORDER
        return commitment == expected


class RangeProofEngine:
    def __init__(self, bit_length: int = 16):
        self.bit_length = bit_length
        self.max_value = (1 << bit_length) - 1

    def generate_proof(self, value: int, blinding: int) -> Dict[str, Any]:
        if not (0 <= value <= self.max_value):
            raise ValueError(f"Value {value} out of bounds [0, {self.max_value}]")

        bit_commitments = []
        bit_blindings = []
        bits = [(value >> i) & 1 for i in range(self.bit_length)]

        for bit in bits:
            r_b = secrets.randbelow(PRIME_ORDER)
            bit_blindings.append(r_b)
            bit_commitments.append(PedersenCommitment.commit(bit, r_b))

        # Fiat-Shamir heuristic transcript challenge
        hasher = hashlib.sha256()
        for c in bit_commitments:
            hasher.update(c.to_bytes(32, byteorder="big"))
        challenge = int.from_bytes(hasher.digest(), byteorder="big") % PRIME_ORDER

        responses = []
        for i in range(self.bit_length):
            b = bits[i]
            r_b = bit_blindings[i]
            resp = (r_b + challenge * b) % PRIME_ORDER
            responses.append(resp)

        sum_blindings = sum((1 << i) * bit_blindings[i] for i in range(self.bit_length)) % PRIME_ORDER
        blinding_delta = (blinding - sum_blindings) % PRIME_ORDER

        return {
            "bit_commitments": bit_commitments,
            "responses": responses,
            "challenge": challenge,
            "blinding_delta": blinding_delta,
            "bit_length": self.bit_length
        }

    def verify_proof(self, commitment: int, proof: Dict[str, Any]) -> bool:
        bit_commitments = proof["bit_commitments"]
        challenge = proof["challenge"]
        blinding_delta = proof["blinding_delta"]

        hasher = hashlib.sha256()
        for c in bit_commitments:
            hasher.update(c.to_bytes(32, byteorder="big"))
        expected_challenge = int.from_bytes(hasher.digest(), byteorder="big") % PRIME_ORDER
        if expected_challenge != challenge:
            return False

        accumulated_commit = 0
        for i, c in enumerate(bit_commitments):
            scale = (1 << i) % PRIME_ORDER
            accumulated_commit = (accumulated_commit + scale * c) % PRIME_ORDER

        target_commit = (accumulated_commit + blinding_delta * GENERATOR_H) % PRIME_ORDER
        return target_commit == (commitment % PRIME_ORDER)
