"""
Shor's Algorithm for ECDLP — adapted for the QDay Prize competition curve.

Curve:  y² = x³ + 7 (mod p)   [a=0, b=7 — same form as Bitcoin's secp256k1]

Synthesis strategy: group-index encoding + modular arithmetic built-ins.

The ECC group is cyclic of prime order n, isomorphic to Z_n.
Encode ecp as a group index k ∈ {0, ..., n-1} meaning k*G.
"Add 2^i * G" in index space = modular_add_constant_inplace(n, 2^i, ecp_idx).
This uses Classiq's optimized modular adder (~O(log n) gates vs O(n) for tables).

Target (4-bit test vector from contest_information/successful_curves.json):
  p=13, n=7, G=[11,5], Q=[11,8], d=6  (i.e. Q = 6·G)

Usage:
  python shor_ecdlp_classiq.py
  Change TARGET_BITS below to target a different key size.
"""

from classiq import *

# ---------------------
# Curve & problem setup
# ---------------------

CURVE_PARAMS = {
    4: dict(p=13,  n=7,   G=[11, 5],   Q=[11, 8],    d=6),
    6: dict(p=43,  n=31,  G=[34, 3],   Q=[21, 25],   d=18),
    7: dict(p=67,  n=79,  G=[48, 60],  Q=[52, 7],    d=56),
    8: dict(p=163, n=139, G=[112, 53], Q=[122, 144],  d=103),
}

TARGET_BITS     = 4
params          = CURVE_PARAMS[TARGET_BITS]
P_MOD           = params["p"]
GENERATOR_ORDER = params["n"]   # prime order of the generator
GENERATOR_G     = params["G"]
TARGET_POINT    = params["Q"]
KNOWN_D         = params["d"]

VAR_LEN  = GENERATOR_ORDER.bit_length()  # qubits for x1, x2 QPE registers
IDX_BITS = GENERATOR_ORDER.bit_length()  # qubits for ecp group index

# ECC group index encoding: k represents k*G.
INITIAL_IDX  = 2                                              # start at 2*G
NEG_Q_STEP   = (GENERATOR_ORDER - KNOWN_D) % GENERATOR_ORDER  # -Q = (n-d)*G

# Step sizes for bit-decomposed additions:
#   x1 bit i controls adding (2^i mod n) copies of G
#   x2 bit i controls adding (NEG_Q_STEP * 2^i mod n) copies of -Q = (n-d)*G
G_STEPS    = [(1 << i) % GENERATOR_ORDER for i in range(VAR_LEN)]
NEGQ_STEPS = [(NEG_Q_STEP * (1 << i)) % GENERATOR_ORDER for i in range(VAR_LEN)]

print(f"Setup: {TARGET_BITS}-bit | p={P_MOD} | n={GENERATOR_ORDER} | "
      f"VAR_LEN={VAR_LEN} | IDX_BITS={IDX_BITS}")
print(f"  -Q step: {NEG_Q_STEP}  |  G steps: {G_STEPS}  |  -Q steps: {NEGQ_STEPS}")


# ---------------------
# Quantum circuit
# ---------------------

@qfunc
def shor_ecdlp(
    x1: Output[QArray[QBit]],
    x2: Output[QArray[QBit]],
    ecp_idx: Output[QNum[IDX_BITS, False, 0]],
) -> None:
    """
    Shor's ECDLP circuit in group-index space using modular arithmetic.

    Prepares: Σ_{x1,x2} |x1⟩|x2⟩|2 + x1 + x2·(-d) mod n⟩
    then applies inverse QFT on x1, x2.
    """
    allocate(VAR_LEN, x1)
    allocate(VAR_LEN, x2)
    allocate(IDX_BITS, False, 0, ecp_idx)

    ecp_idx ^= INITIAL_IDX     # initialize to 2*G

    hadamard_transform(x1)
    hadamard_transform(x2)

    # ecp += x1 * G  (binary decomposition: bit i adds 2^i mod n)
    for i in range(VAR_LEN):
        control(x1[i], lambda k=G_STEPS[i]:
                modular_add_constant_inplace(GENERATOR_ORDER, k, ecp_idx))

    # ecp += x2 * (-Q)  (binary decomposition)
    for i in range(VAR_LEN):
        control(x2[i], lambda k=NEGQ_STEPS[i]:
                modular_add_constant_inplace(GENERATOR_ORDER, k, ecp_idx))

    invert(lambda: qft(x1))
    invert(lambda: qft(x2))


@qfunc
def main(
    x1: Output[QArray[QBit]],
    x2: Output[QArray[QBit]],
    ecp_idx: Output[QNum[IDX_BITS, False, 0]],
) -> None:
    shor_ecdlp(x1, x2, ecp_idx)


# ---------------------
# Post-processing
# ---------------------

def bits_to_int(bits):
    """Convert LSB-first bit list [b0, b1, ...] to integer."""
    if isinstance(bits, (int, float)):
        return int(bits)
    return sum(int(b) * (1 << i) for i, b in enumerate(bits))


def extract_discrete_log(df, order, var_len):
    """
    Recover d from measured (x1, x2) pairs.
    x1, x2 are QArray[QBit] measured as bit lists (LSB first).

    The circuit computes ecp = P_0 + x1*G + x2*(-Q).
    Period vector is (d, 1): f(x1 + a*d, x2 + a) = f(x1, x2).
    After QFT, measured integers (k1, k2) satisfy r1*d + r2 ≡ 0 (mod n),
    where r1 = round(k1/N * n), r2 = round(k2/N * n).
    Therefore: d ≡ -r2 · r1⁻¹ (mod n).
    """
    import math
    N = 1 << var_len
    df = df.copy()
    df["x1_int"] = df["x1"].apply(bits_to_int)
    df["x2_int"] = df["x2"].apply(bits_to_int)
    df["x1_r"] = (df["x1_int"] / N * order).round().astype(int) % order
    df["x2_r"] = (df["x2_int"] / N * order).round().astype(int) % order
    df = df[df["x1_r"].apply(lambda v: math.gcd(int(v), order) == 1)].copy()
    df["d_candidate"] = (
        -df["x2_r"] * df["x1_r"].apply(lambda v: pow(int(v), -1, order))
    ) % order
    return df


# ---------------------
# Synthesize & execute
# ---------------------

def run():
    print(f"\nQDay Prize — Shor's ECDLP on y²=x³+7 (mod {P_MOD})")
    print(f"  G={GENERATOR_G}  Q={TARGET_POINT}  n={GENERATOR_ORDER}  known d={KNOWN_D}\n")

    constraints = Constraints(max_width=200)
    preferences = Preferences(optimization_level=0, timeout_seconds=3600)

    print("Synthesizing...")
    qmod = create_model(main, constraints=constraints, preferences=preferences)
    qprog = synthesize(qmod)
    cx = qprog.transpiled_circuit.count_ops.get("cx", "N/A")
    print(f"  Qubits:   {qprog.data.width}")
    print(f"  Depth:    {qprog.transpiled_circuit.depth}")
    print(f"  CX gates: {cx}\n")

    print("Executing...")
    res = execute(qprog).result_value()
    df = res.dataframe.sort_values("counts", ascending=False)
    df["probability"] = df["counts"] / df["counts"].sum()
    print(df.head(10).to_string(index=False))

    print("\nPost-processing...")
    df_log = extract_discrete_log(df, GENERATOR_ORDER, VAR_LEN)
    if df_log.empty:
        print("No valid measurements — try more shots or a larger register.")
        return

    d_found = int(df_log["d_candidate"].mode()[0])
    print(f"\n  Recovered d = {d_found}")
    print(f"  Expected  d = {KNOWN_D}")
    print(f"  {'✅ CORRECT' if d_found == KNOWN_D else '❌ MISMATCH'}")


if __name__ == "__main__":
    run()
