"""
Shor's Algorithm for ECDLP — adapted for the QDay Prize competition curve.

Curve:  y² = x³ + 7 (mod p)   [a=0, b=7 — same form as Bitcoin's secp256k1]

Adapted from the Classiq library notebook:
  resources/elliptic_curve_discrete_log.ipynb
  https://github.com/Classiq/classiq-library/blob/main/algorithms/number_theory_and_cryptography/elliptic_curves/elliptic_curve_discrete_log.ipynb

Target (4-bit test vector from contest_information/successful_curves.json):
  p=13, n=7, G=[11,5], Q=[11,8], d=6  (i.e. Q = 6·G)

Usage:
  Set CLASSIQ_API_KEY in your environment, then run:
    python shor_ecdlp_classiq.py

  To target a different key size, change TARGET_BITS below.
"""

import math
import numpy as np
from classiq import *
from classiq.qmod.symbolic import subscript

# ---------------------
# Classical Helpers
# ---------------------

class EllipticCurve:
    """Elliptic curve of the form y² = x³ + a·x + b (mod p)."""
    def __init__(self, p, a, b):
        self.p = p
        self.a = a
        self.b = b


def point_double(P, curve):
    """Classical point doubling: returns 2·P."""
    p, a = curve.p, curve.a
    x, y = P
    s = (3 * x * x + a) * pow(2 * y, -1, p) % p
    xr = (s * s - 2 * x) % p
    yr = (y - s * (x - xr)) % p
    return [xr, (p - yr) % p]


# ---------------------
# Curve & Problem Setup
# ---------------------

# Competition curve: y² = x³ + 7 (mod p), a=0 for all instances.
# Edit TARGET_BITS to target a different key size from successful_curves.json.
CURVE_PARAMS = {
    4: dict(p=13,  n=7,   G=[11, 5],   Q=[11, 8],    d=6),
    6: dict(p=43,  n=31,  G=[34, 3],   Q=[21, 25],   d=18),
    7: dict(p=67,  n=79,  G=[48, 60],  Q=[52, 7],    d=56),
    8: dict(p=163, n=139, G=[112, 53], Q=[122, 144],  d=103),
}

TARGET_BITS = 4
params = CURVE_PARAMS[TARGET_BITS]

CURVE           = EllipticCurve(p=params["p"], a=0, b=7)
GENERATOR_G     = params["G"]
GENERATOR_ORDER = params["n"]
TARGET_POINT    = params["Q"]   # public key — the ECDLP input
KNOWN_D         = params["d"]   # known answer, used only for verification

# INITIAL_POINT: any non-identity curve point used to initialize the quantum ECP
# register (avoids representing the identity/point-at-infinity in the circuit).
# Using 2·G as a safe default.
INITIAL_POINT = point_double(GENERATOR_G, CURVE)


# ---------------------
# Quantum Circuit (Classiq Qmod)
# ---------------------

class EllipticCurvePoint(QStruct):
    x: QNum[CURVE.p.bit_length()]
    y: QNum[CURVE.p.bit_length()]


@qperm
def mock_modular_inverse(x: Const[QNum], result: QNum, modulus: int) -> None:
    """
    Lookup-table modular inverse: |x⟩|0⟩ → |x⟩|x⁻¹ mod modulus⟩.
    Sets result to 0 when the inverse does not exist.
    Practical for small p; avoids the cost of full quantum modular inversion.
    """
    inverse_table = lookup_table(
        lambda _x: pow(_x, -1, modulus) if math.gcd(_x, modulus) == 1 else 0, x
    )
    result ^= subscript(inverse_table, x)


@qperm
def ec_point_add(
    ecp: EllipticCurvePoint,
    G: list[int],
    p: int,
) -> None:
    """
    In-place quantum ECC point addition: ecp ← ecp + G (mod p).
    G is a classically known point; ecp is the quantum register.

    Implements the Weierstrass addition formula reversibly using mock_modular_inverse.
    Assumes ecp ≠ G and ecp ≠ -G (no special-case handling for doubling or identity).
    """
    n = CURVE.p.bit_length()
    slope = QNum()
    allocate(n, slope)
    t0 = QNum()
    allocate(n, t0)

    Gx, Gy = G[0], G[1]

    # Step 1: y ← y1 - Gy
    modular_add_constant_inplace(p, (-Gy) % p, ecp.y)
    # Step 2: x ← x1 - Gx
    modular_add_constant_inplace(p, (-Gx) % p, ecp.x)
    # Step 3: slope ← (y1 - Gy) / (x1 - Gx) mod p
    within_apply(
        lambda: mock_modular_inverse(ecp.x, t0, p),
        lambda: modular_multiply(p, t0, ecp.y, slope),
    )
    # Step 4: y ← 0  (uncompute numerator)
    within_apply(
        lambda: modular_multiply(p, slope, ecp.x, t0),
        lambda: inplace_xor(t0, ecp.y),
    )
    # Step 5: x ← Gx - x3
    within_apply(
        lambda: modular_square(p, slope, t0),
        lambda: (
            modular_subtract_inplace(p, t0, ecp.x),
            modular_negate_inplace(p, ecp.x),
            modular_add_constant_inplace(p, (3 * Gx) % p, ecp.x),
        ),
    )
    # Step 6: y ← y3 + Gy
    modular_multiply(p, slope, ecp.x, ecp.y)
    # Step 7: uncompute slope
    t1 = QNum()
    within_apply(
        lambda: mock_modular_inverse(ecp.x, t0, p),
        lambda: within_apply(
            lambda: (allocate(CURVE.p.bit_length(), t1),
                     modular_multiply(p, t0, ecp.y, t1)),
            lambda: inplace_xor(t1, slope),
        ),
    )
    free(slope)
    # Step 8: final coordinate adjustments → ecp = result of addition
    modular_add_constant_inplace(p, (-Gy) % p, ecp.y)
    modular_negate_inplace(p, ecp.x)
    modular_add_constant_inplace(p, Gx, ecp.x)


@qperm
def ec_scalar_mult_add(
    ecp: EllipticCurvePoint,
    k: QArray[QBit],
    P: list[int],
    p: int,
    a: int,
    b: int,
) -> None:
    """
    Quantum scalar multiplication: ecp ← ecp + k·P.
    Uses controlled point addition for each bit of k (double-and-add).
    """
    current_power = P.copy()
    for i in range(k.size):
        control(k[i], lambda: ec_point_add(ecp, current_power, p))
        if i < k.size - 1:
            current_power = point_double(current_power, EllipticCurve(p, a, b))


@qfunc
def shor_ecdlp(
    x1: Output[QNum],
    x2: Output[QNum],
    ecp: Output[EllipticCurvePoint],
    P_0: list[int],
    G: list[int],
    P_target: list[int],
) -> None:
    """
    Shor's ECDLP quantum subroutine.

    Prepares:  Σ_{x1,x2} |x1⟩|x2⟩|P_0 + x1·G - x2·Q⟩
    then applies inverse QFT on x1, x2.

    Each valid measurement gives (x1, x2) satisfying x1 ≡ d·x2 (mod n),
    from which d is recovered classically.
    """
    var_len = GENERATOR_ORDER.bit_length()
    allocate(var_len, False, var_len, x1)
    allocate(var_len, False, var_len, x2)

    allocate(ecp)
    ecp.x ^= P_0[0]
    ecp.y ^= P_0[1]

    hadamard_transform(x1)
    hadamard_transform(x2)

    # ecp = P_0 + x1·G
    ec_scalar_mult_add(ecp, x1, G, CURVE.p, CURVE.a, CURVE.b)
    # ecp = P_0 + x1·G + x2·(-Q)
    neg_target = [P_target[0], (-P_target[1]) % CURVE.p]
    ec_scalar_mult_add(ecp, x2, neg_target, CURVE.p, CURVE.a, CURVE.b)

    # Inverse QFT for period extraction
    invert(lambda: qft(x1))
    invert(lambda: qft(x2))


@qfunc
def main(x1: Output[QNum], x2: Output[QNum], ecp: Output[EllipticCurvePoint]) -> None:
    shor_ecdlp(x1, x2, ecp, INITIAL_POINT, GENERATOR_G, TARGET_POINT)


# ---------------------
# Post-Processing
# ---------------------

def extract_discrete_log(df, order):
    """
    Recover d from measured (x1, x2) pairs.

    Each valid pair satisfies: x1 + d·x2 ≡ 0 (mod n)
    → d ≡ -x1 · x2⁻¹ (mod n)

    Filters rows where gcd(x2_rounded, n) == 1 so the inverse exists.
    Returns the DataFrame with a 'd_candidate' column.
    """
    df = df.copy()
    df["x1_r"] = (df["x1"] * order).round().astype(int) % order
    df["x2_r"] = (df["x2"] * order).round().astype(int) % order
    df = df[np.gcd(df["x2_r"], order) == 1].copy()
    df["d_candidate"] = (
        -df["x1_r"] * df["x2_r"].apply(lambda x: pow(int(x), -1, order))
    ) % order
    return df


# ---------------------
# Main: Synthesize & Execute
# ---------------------

def run():
    print(f"QDay Prize — Shor's ECDLP on y² = x³ + 7 (mod {CURVE.p})")
    print(f"  {TARGET_BITS}-bit key | G={GENERATOR_G} | Q={TARGET_POINT} | n={GENERATOR_ORDER}")
    print(f"  Known d={KNOWN_D} (for verification only)\n")

    constraints = Constraints(optimization_parameter="width")
    preferences = Preferences(timeout_seconds=3600, optimization_level=1, qasm3=True)

    print("Synthesizing...")
    qmod = create_model(main, constraints=constraints, preferences=preferences)
    qprog = synthesize(qmod)
    print(f"  Qubits: {qprog.data.width}")
    print(f"  Depth:  {qprog.transpiled_circuit.depth}\n")

    print("Executing...")
    res = execute(qprog).result_value()
    df = res.dataframe.sort_values("counts", ascending=False)
    df["probability"] = df["counts"] / df["counts"].sum()
    print(df.head(10).to_string(index=False))

    print("\nPost-processing...")
    df_log = extract_discrete_log(df, GENERATOR_ORDER)
    if df_log.empty:
        print("No valid measurements — try more shots or a larger register.")
        return

    d_found = int(df_log["d_candidate"].mode()[0])
    print(f"\n  Recovered d = {d_found}")
    print(f"  Expected  d = {KNOWN_D}")
    print(f"  {'✅ CORRECT' if d_found == KNOWN_D else '❌ MISMATCH'}")


if __name__ == "__main__":
    run()
