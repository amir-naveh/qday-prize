"""
Classical ECC implementation for the QDay Prize competition curve.

Curve: y^2 = x^3 + 7 (mod p)

Provides point addition, scalar multiplication, and ECDLP brute-force solver.
Used as a classical baseline and ground truth for verifying quantum results.
"""

import json
from pathlib import Path


# ---------------------
# ECC Arithmetic
# ---------------------

def point_add(P, Q, p):
    """Add two points on y^2 = x^3 + 7 (mod p). Identity element is None."""
    if P is None:
        return Q
    if Q is None:
        return P
    if P[0] == Q[0]:
        if (P[1] + Q[1]) % p == 0:
            return None  # P + (-P) = identity
        # Point doubling (a=0)
        s = (3 * P[0] * P[0]) * pow(2 * P[1], -1, p) % p
    else:
        s = (Q[1] - P[1]) * pow(Q[0] - P[0], -1, p) % p
    x_r = (s * s - P[0] - Q[0]) % p
    y_r = (s * (P[0] - x_r) - P[1]) % p
    return (x_r, y_r)


def scalar_mult(k, P, p):
    """Compute k*P via double-and-add."""
    R = None
    Q = P
    while k > 0:
        if k & 1:
            R = point_add(R, Q, p)
        Q = point_add(Q, Q, p)
        k >>= 1
    return R


def solve_ecdlp_brute(G, Q, n, p):
    """
    Brute-force solve Q = d*G for d in [1, n-1].
    Only feasible for small key sizes (up to ~20 bits).
    Returns d if found, else None.
    """
    current = G
    for d in range(1, n):
        if current == Q:
            return d
        current = point_add(current, G, p)
    return None


# ---------------------
# Verification
# ---------------------

def verify_test_vectors(json_path):
    """
    Load test vectors from successful_curves.json and verify:
    1. scalar_mult(d, G, p) == Q  (key pair is consistent)
    2. solve_ecdlp_brute(G, Q, n, p) == d  (ECDLP solver recovers correct key)
    """
    vectors = json.loads(Path(json_path).read_text())
    print(f"Verifying {len(vectors)} test vectors...\n")

    all_passed = True
    for v in vectors:
        bits = v["bit_length"]
        p = v["prime"]
        n = v["subgroup_order"]
        G = tuple(v["generator_point"])
        d = v["private_key"]
        Q = tuple(v["public_key"])

        # Check 1: d*G == Q
        Q_computed = scalar_mult(d, G, p)
        keypair_ok = Q_computed == Q

        # Check 2: ECDLP solver recovers d
        d_recovered = solve_ecdlp_brute(G, Q, n, p)
        ecdlp_ok = d_recovered == d

        status = "PASS" if (keypair_ok and ecdlp_ok) else "FAIL"
        if status == "FAIL":
            all_passed = False

        print(f"  [{status}] {bits}-bit | p={p} | d={d} | "
              f"keypair={'ok' if keypair_ok else 'FAIL'} | "
              f"ecdlp={'ok' if ecdlp_ok else f'got {d_recovered}'}")

    print(f"\n{'All tests passed.' if all_passed else 'SOME TESTS FAILED.'}")
    return all_passed


if __name__ == "__main__":
    json_path = Path(__file__).parent.parent / "contest_information" / "successful_curves.json"
    verify_test_vectors(json_path)
