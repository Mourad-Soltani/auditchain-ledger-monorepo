import secrets
from typing import List, Tuple

FIELD_PRIME = 2**256 - 189


def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y


def mod_inverse(k: int, p: int) -> int:
    k = k % p
    gcd, x, _ = extended_gcd(k, p)
    if gcd != 1:
        raise ValueError("Multiplicative inverse does not exist")
    return x % p


class ThresholdSecretSharer:
    def __init__(self, threshold: int, total_shares: int):
        if threshold > total_shares or threshold < 2:
            raise ValueError("Invalid threshold parameters")
        self.k = threshold
        self.n = total_shares

    def split_secret(self, secret: int) -> List[Tuple[int, int]]:
        if not (0 <= secret < FIELD_PRIME):
            raise ValueError("Secret must lie in the finite field")
        coefficients = [secret] + [secrets.randbelow(FIELD_PRIME) for _ in range(self.k - 1)]
        shares = []
        for x in range(1, self.n + 1):
            y = 0
            for exp, coeff in enumerate(coefficients):
                y = (y + coeff * pow(x, exp, FIELD_PRIME)) % FIELD_PRIME
            shares.append((x, y))
        return shares

    @staticmethod
    def reconstruct_secret(shares: List[Tuple[int, int]]) -> int:
        if len(shares) < 2:
            raise ValueError("Insufficient shares to reconstruct")
        secret = 0
        for i, (xi, yi) in enumerate(shares):
            numerator = 1
            denominator = 1
            for j, (xj, _) in enumerate(shares):
                if i == j:
                    continue
                numerator = (numerator * (-xj)) % FIELD_PRIME
                denominator = (denominator * (xi - xj)) % FIELD_PRIME
            basis = (numerator * mod_inverse(denominator, FIELD_PRIME)) % FIELD_PRIME
            secret = (secret + yi * basis) % FIELD_PRIME
        return secret
