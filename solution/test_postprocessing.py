"""
Classical validation of Shor's ECDLP post-processing.

Simulates the theoretical quantum measurement distribution for the 4-bit
competition test vector and verifies that the post-processing in
shor_ecdlp_classiq.py correctly recovers d.

Runs without a Classiq API key — pure Python.

Theory:
  For order n and discrete log d, the Shor ECDLP circuit produces
  measurement pairs (x1, x2) concentrated around rational approximations
  to (s1/n, s2/n) where s1 + d·s2 ≡ 0 (mod n).
  Post-processing recovers: d ≡ -x1_rounded · x2_rounded⁻¹ (mod n)
"""

import math
import numpy as np
import pandas as pd


# ---------------------
# Test Parameters
# ---------------------

CURVE_PARAMS = {
    4:  dict(p=13,  n=7,   G=[11, 5],   Q=[11, 8],    d=6),
    6:  dict(p=43,  n=31,  G=[34, 3],   Q=[21, 25],   d=18),
    7:  dict(p=67,  n=79,  G=[48, 60],  Q=[52, 7],    d=56),
    8:  dict(p=163, n=139, G=[112, 53], Q=[122, 144],  d=103),
}


# ---------------------
# Classical ECC (copied from ecc_classical.py for self-containment)
# ---------------------

def point_add(P, Q, p):
    if P is None: return Q
    if Q is None: return P
    if P[0] == Q[0]:
        if (P[1] + Q[1]) % p == 0: return None
        s = (3 * P[0] * P[0]) * pow(2 * P[1], -1, p) % p
    else:
        s = (Q[1] - P[1]) * pow(Q[0] - P[0], -1, p) % p
    xr = (s * s - P[0] - Q[0]) % p
    yr = (s * (P[0] - xr) - P[1]) % p
    return (xr, yr)


def scalar_mult(k, P, p):
    R, Q = None, P
    while k > 0:
        if k & 1: R = point_add(R, Q, p)
        Q = point_add(Q, Q, p)
        k >>= 1
    return R


# ---------------------
# Simulate Quantum Measurement Distribution
# ---------------------

def simulate_measurement_distribution(n, d, var_bits):
    """
    Classically compute the ideal (noiseless) quantum measurement probability
    distribution over (x1, x2) pairs for Shor's ECDLP with given n and d.

    Each valid (s1, s2) with s1 + d·s2 ≡ 0 (mod n) contributes equal amplitude.
    The measured floating-point values are x1 ≈ s1/n, x2 ≈ s2/n.

    Returns a DataFrame with columns: x1, x2, counts, probability.
    """
    rows = []
    for s2 in range(n):
        s1 = (-d * s2) % n
        # Simulate as fractional values (what Classiq returns after QFT)
        x1 = s1 / n
        x2 = s2 / n
        rows.append({"x1": x1, "x2": x2, "counts": 100})  # equal weight

    df = pd.DataFrame(rows)
    df["probability"] = df["counts"] / df["counts"].sum()
    return df


# ---------------------
# Post-Processing (mirrors shor_ecdlp_classiq.py)
# ---------------------

def extract_discrete_log(df, order):
    df = df.copy()
    df["x1_r"] = (df["x1"] * order).round().astype(int) % order
    df["x2_r"] = (df["x2"] * order).round().astype(int) % order
    df = df[np.gcd(df["x2_r"], order) == 1].copy()
    df["d_candidate"] = (
        -df["x1_r"] * df["x2_r"].apply(lambda x: pow(int(x), -1, order))
    ) % order
    return df


# ---------------------
# Verification
# ---------------------

def verify_valid_pairs(n, d):
    """
    Verify all (s1, s2) pairs satisfying s1 + d·s2 ≡ 0 (mod n),
    and confirm each one individually yields the correct d via post-processing.
    """
    print(f"  Valid (s1, s2) pairs and individual d recovery:")
    all_correct = True
    for s2 in range(n):
        s1 = (-d * s2) % n
        if s2 == 0:
            print(f"    s1={s1}, s2={s2}  →  skip (x2=0, no inverse)")
            continue
        if math.gcd(s2, n) != 1:
            print(f"    s1={s1}, s2={s2}  →  skip (gcd({s2},{n})≠1)")
            continue
        d_recovered = (-s1 * pow(s2, -1, n)) % n
        ok = d_recovered == d
        if not ok:
            all_correct = False
        print(f"    s1={s1}, s2={s2}  →  d={d_recovered}  {'✅' if ok else '❌'}")
    return all_correct


def run_test(bits):
    params = CURVE_PARAMS[bits]
    p, n, G, Q, d = params["p"], params["n"], params["G"], params["Q"], params["d"]

    print(f"\n{'='*55}")
    print(f"Test: {bits}-bit | p={p} | n={n} | d={d}")
    print(f"  G={G}  Q={Q}")

    # 1. Verify keypair is consistent
    Q_check = scalar_mult(d, tuple(G), p)
    assert Q_check == tuple(Q), f"Keypair mismatch: {Q_check} != {Q}"
    print(f"  Keypair check: ✅")

    # 2. Verify all (s1, s2) pairs recover d correctly
    all_pairs_ok = verify_valid_pairs(n, d)

    # 3. Simulate full measurement distribution and run post-processing
    var_bits = n.bit_length()
    df = simulate_measurement_distribution(n, d, var_bits)
    df_log = extract_discrete_log(df, n)

    if df_log.empty:
        print(f"  Post-processing: ❌  No valid rows")
        return False

    candidates = df_log["d_candidate"].value_counts()
    d_found = int(candidates.index[0])
    correct = (d_found == d)
    print(f"  Post-processing recovered d={d_found}  {'✅' if correct else '❌'}")
    return all_pairs_ok and correct


if __name__ == "__main__":
    print("Shor's ECDLP Post-Processing Validation")
    print("Tests that classical post-processing correctly recovers d")
    print("from ideal quantum measurement pairs — no Classiq API needed.\n")

    results = {}
    for bits in CURVE_PARAMS:
        results[bits] = run_test(bits)

    print(f"\n{'='*55}")
    print("Summary:")
    all_passed = True
    for bits, ok in results.items():
        print(f"  {bits}-bit: {'PASS ✅' if ok else 'FAIL ❌'}")
        if not ok:
            all_passed = False
    print(f"\n{'All tests passed.' if all_passed else 'SOME TESTS FAILED.'}")
