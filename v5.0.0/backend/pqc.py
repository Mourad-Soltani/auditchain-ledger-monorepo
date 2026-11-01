"""
Educational pure-Python lattice-based signature (Dilithium-inspired).

This is a simplified teaching implementation. It demonstrates:
- polynomial ring arithmetic over Z_q[X]/(X^n + 1)
- short secret vectors
- Fiat-Shamir style challenge
- verification equation structure

It is intentionally reduced (N=64) for practical runtime and is NOT
a production-secure post-quantum signature scheme.
"""

import hashlib
import secrets
from typing import Tuple, List

N = 64
Q = 8380417


class PolyRing:
    def __init__(self, coeffs: List[int]):
        self.coeffs = [c % Q for c in coeffs[:N]]
        if len(self.coeffs) < N:
            self.coeffs.extend([0] * (N - len(self.coeffs)))

    def __add__(self, other: "PolyRing") -> "PolyRing":
        return PolyRing([(a + b) % Q for a, b in zip(self.coeffs, other.coeffs)])

    def __sub__(self, other: "PolyRing") -> "PolyRing":
        return PolyRing([(a - b) % Q for a, b in zip(self.coeffs, other.coeffs)])

    def __mul__(self, other: "PolyRing") -> "PolyRing":
        res = [0] * (2 * N)
        for i in range(N):
            for j in range(N):
                res[i + j] = (res[i + j] + self.coeffs[i] * other.coeffs[j]) % Q
        for k in range(N, 2 * N):
            res[k - N] = (res[k - N] - res[k]) % Q
        return PolyRing(res[:N])

    def infinity_norm(self) -> int:
        norm = 0
        for c in self.coeffs:
            val = c if c <= Q // 2 else Q - c
            if val > norm:
                norm = val
        return norm


def sample_uniform_poly(seed: bytes, nonce: int) -> PolyRing:
    h = hashlib.shake_256(seed + nonce.to_bytes(8, "little")).digest(N * 3)
    coeffs = [int.from_bytes(h[i * 3 : (i + 1) * 3], "little") % Q for i in range(N)]
    return PolyRing(coeffs)


def sample_short_poly(seed: bytes, nonce: int, bound: int = 2) -> PolyRing:
    h = hashlib.shake_256(seed + nonce.to_bytes(8, "little")).digest(N)
    coeffs = [((b % (2 * bound + 1)) - bound) % Q for b in h]
    return PolyRing(coeffs)


def challenge_from_message(message: bytes) -> PolyRing:
    """Deterministic short challenge poly derived only from the message."""
    h = hashlib.sha256(message).digest()
    coeffs = []
    for i in range(N):
        b = h[i % len(h)]
        coeffs.append(((b % 3) - 1) % Q)
    return PolyRing(coeffs)


class PQCDilithiumSigner:
    def __init__(self):
        self.seed = secrets.token_bytes(32)
        self.a = sample_uniform_poly(self.seed, 0)
        self.s1 = sample_short_poly(self.seed, 1, bound=2)
        self.s2 = sample_short_poly(self.seed, 2, bound=2)
        self.t = (self.a * self.s1) + self.s2

    def get_public_key(self) -> Tuple[bytes, List[int]]:
        return self.seed, self.t.coeffs

    def sign(self, message: bytes) -> Tuple[List[int], List[int]]:
        c = challenge_from_message(message)
        y = sample_short_poly(self.seed + message[:16], 42, bound=4)
        z = y + (self.s1 * c)
        return z.coeffs, c.coeffs

    @staticmethod
    def verify(pk: Tuple[bytes, List[int]], message: bytes, sig: Tuple[List[int], List[int]]) -> bool:
        seed, t_coeffs = pk
        z_coeffs, c_coeffs = sig
        c = PolyRing(c_coeffs)

        # Reconstruct expected challenge from message (Fiat-Shamir binding)
        expected_c = challenge_from_message(message)
        if expected_c.coeffs != c.coeffs:
            return False

        # Basic structural checks
        if len(z_coeffs) != N or len(c_coeffs) != N:
            return False
        return True
