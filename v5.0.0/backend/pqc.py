import hashlib
import secrets
from typing import Tuple, List

N = 256
Q = 8380417
D = 13
GAMMA1 = (Q - 1) // 16
GAMMA2 = GAMMA1 // 2
BETA = 78


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
    h = hashlib.shake_256(seed + nonce.to_bytes(2, "little")).digest(N * 3)
    coeffs = []
    for i in range(N):
        val = int.from_bytes(h[i * 3 : (i + 1) * 3], "little") % Q
        coeffs.append(val)
    return PolyRing(coeffs)


def sample_short_poly(seed: bytes, nonce: int, bound: int = 2) -> PolyRing:
    h = hashlib.shake_256(seed + nonce.to_bytes(2, "little")).digest(N)
    coeffs = []
    for b in h:
        val = (b % (2 * bound + 1)) - bound
        coeffs.append(val % Q)
    return PolyRing(coeffs)


class PQCDilithiumSigner:
    def __init__(self):
        self.seed = secrets.token_bytes(32)
        self.a = sample_uniform_poly(self.seed, 0)
        self.s1 = sample_short_poly(self.seed, 1)
        self.s2 = sample_short_poly(self.seed, 2)
        self.t = (self.a * self.s1) + self.s2

    def get_public_key(self) -> Tuple[bytes, List[int]]:
        return self.seed, self.t.coeffs

    def sign(self, message: bytes) -> Tuple[List[int], List[int]]:
        nonce = 100
        while True:
            y = sample_short_poly(secrets.token_bytes(32), nonce, bound=GAMMA1)
            w = self.a * y
            msg_hash = hashlib.sha256(message + bytes([c % 256 for c in w.coeffs])).digest()
            c_coeffs = [((b % 3) - 1) % Q for b in msg_hash[:N]]
            if len(c_coeffs) < N:
                c_coeffs.extend([0] * (N - len(c_coeffs)))
            c = PolyRing(c_coeffs)
            z = y + (self.s1 * c)
            if z.infinity_norm() < (GAMMA1 - BETA):
                return z.coeffs, c.coeffs
            nonce += 1

    @staticmethod
    def verify(pk: Tuple[bytes, List[int]], message: bytes, sig: Tuple[List[int], List[int]]) -> bool:
        seed, t_coeffs = pk
        z_coeffs, c_coeffs = sig
        a = sample_uniform_poly(seed, 0)
        t = PolyRing(t_coeffs)
        z = PolyRing(z_coeffs)
        c = PolyRing(c_coeffs)
        if z.infinity_norm() >= (GAMMA1 - BETA):
            return False
        w_prime = (a * z) - (t * c)
        msg_hash = hashlib.sha256(message + bytes([c % 256 for c in w_prime.coeffs])).digest()
        expected_c = [((b % 3) - 1) % Q for b in msg_hash[:N]]
        if len(expected_c) < N:
            expected_c.extend([0] * (N - len(expected_c)))
        return PolyRing(expected_c).coeffs == c.coeffs
