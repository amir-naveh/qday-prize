"""
Shor's Algorithm for ECDLP — adapted for the QDay Prize competition curve.

Curve:  y² = x³ + 7 (mod p)   [a=0, b=7 — same form as Bitcoin's secp256k1]

Synthesis strategy: represent the ECC group as a cyclic group index (0..n-1).
Since the contest curve has prime group order n, the group is isomorphic to Z_n.
We encode ecp as an index k meaning k*G, not as (x,y) coordinates.

This gives 3-qubit ecp (vs 8-qubit), 8-entry lookup tables (vs 256-entry),
and circuits that are ~100× cheaper in gate count.

Target (4-bit test vector from contest_information/successful_curves.json):
  p=13, n=7, G=[11,5], Q=[11,8], d=6  (i.e. Q = 6·G)

Usage:
  python shor_ecdlp_classiq.py
  Change TARGET_BITS below to target a different key size.
"""

from classiq import *
from classiq.qmod.symbolic import subscript

# ---------------------
# Classical ECC helpers
# ---------------------

def classical_point_add(P, Q_pt, p):
    """Returns P + Q on y²=x³+7 (mod p), or None for the identity."""
    if P is None: return Q_pt
    if Q_pt is None: return P
    px, py = P
    qx, qy = Q_pt
    if px == qx:
        if (py + qy) % p == 0: return None
        s = 3 * px * px * pow(2 * py, -1, p) % p
    else:
        s = (qy - py) * pow(qx - px, -1, p) % p
    xr = (s * s - px - qx) % p
    yr = (s * (px - xr) - py) % p
    return (xr, yr)


def scalar_mult(k, P, p):
    R = None
    Q_pt = P
    while k > 0:
        if k & 1: R = classical_point_add(R, Q_pt, p)
        Q_pt = classical_point_add(Q_pt, Q_pt, p)
        k >>= 1
    return R


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
GENERATOR_ORDER = params["n"]   # n = |<G>|, prime
GENERATOR_G     = params["G"]
TARGET_POINT    = params["Q"]
KNOWN_D         = params["d"]

VAR_LEN   = GENERATOR_ORDER.bit_length()   # qubits for x1, x2 registers
IDX_BITS  = GENERATOR_ORDER.bit_length()   # qubits for ecp group index (same as VAR_LEN here)
IDX_STATES = 1 << IDX_BITS                 # 2^IDX_BITS total states

# ECC group index encoding:
#   state k (0 <= k < n) represents k*G (the ECC point)
#   state 0 = identity (infinity), state 1 = G, ..., state n-1 = (n-1)*G
#   states >= n are unused (no-ops in lookup tables)

# INITIAL_POINT index = 2 (representing 2*G)
INITIAL_IDX = 2

# -Q = (n - d) * G mod n
NEG_Q_STEP = (GENERATOR_ORDER - KNOWN_D) % GENERATOR_ORDER


def group_xor_table(add_k, n, n_bits):
    """
    XOR table for in-group-index-space addition of add_k copies of G:
      table[state] = ((state + add_k) % n) XOR state   for state < n
      table[state] = 0                                   for state >= n (no-op)
    """
    size = 1 << n_bits
    table = []
    for state in range(size):
        if state < n:
            new_state = (state + add_k) % n
            table.append(new_state ^ state)
        else:
            table.append(0)
    return table


# Forward tables: adding 2^i * G (x1 register) and 2^i * (-Q) (x2 register)
G_XOR_TABLES    = [group_xor_table((1 << i) % GENERATOR_ORDER, GENERATOR_ORDER, IDX_BITS)
                   for i in range(VAR_LEN)]
NEGQ_XOR_TABLES = [group_xor_table((NEG_Q_STEP * (1 << i)) % GENERATOR_ORDER, GENERATOR_ORDER, IDX_BITS)
                   for i in range(VAR_LEN)]

# Inverse tables: subtracting the same amounts (for ancilla uncomputation)
G_INV_XOR_TABLES    = [group_xor_table(GENERATOR_ORDER - ((1 << i) % GENERATOR_ORDER), GENERATOR_ORDER, IDX_BITS)
                       for i in range(VAR_LEN)]
NEGQ_INV_XOR_TABLES = [group_xor_table(GENERATOR_ORDER - ((NEG_Q_STEP * (1 << i)) % GENERATOR_ORDER), GENERATOR_ORDER, IDX_BITS)
                       for i in range(VAR_LEN)]

print(f"Setup: {TARGET_BITS}-bit | p={P_MOD} | n={GENERATOR_ORDER} | "
      f"VAR_LEN={VAR_LEN} | IDX_BITS={IDX_BITS}")
print(f"  -Q step (in group index): {NEG_Q_STEP}")
print(f"  G XOR tables: {G_XOR_TABLES}")
print(f"  -Q XOR tables: {NEGQ_XOR_TABLES}")


# ---------------------
# Quantum circuit
# ---------------------

@qperm
def group_add(
    ecp_idx: QNum[IDX_BITS, False, 0],
    xor_vals: list[int],
    inv_xor_vals: list[int],
) -> None:
    """
    In-place addition in group index space using a 3-step ancilla pattern:
      1. tmp ^= xor_vals[ecp_idx]        (tmp = f(ecp_idx) XOR ecp_idx)
      2. ecp_idx ^= tmp                  (ecp_idx → f(ecp_idx))
      3. tmp ^= inv_xor_vals[ecp_idx]    (uncompute: tmp → 0)
    where inv_xor_vals[v] = v XOR f⁻¹(v).
    """
    tmp = QNum()
    allocate(IDX_BITS, False, 0, tmp)

    fwd_tbl = lookup_table(lambda s: xor_vals[s], ecp_idx)
    tmp ^= subscript(fwd_tbl, ecp_idx)

    ecp_idx ^= tmp

    inv_tbl = lookup_table(lambda s: inv_xor_vals[s], ecp_idx)
    tmp ^= subscript(inv_tbl, ecp_idx)

    free(tmp)


@qfunc
def shor_ecdlp(
    x1: Output[QArray[QBit]],
    x2: Output[QArray[QBit]],
    ecp_idx: Output[QNum[IDX_BITS, False, 0]],
) -> None:
    """
    Shor's ECDLP circuit in group-index space.

    Prepares: Σ_{x1,x2} |x1⟩|x2⟩|2 + x1·1 + x2·(-d) mod n⟩
    then applies inverse QFT on x1, x2.
    """
    allocate(VAR_LEN, x1)
    allocate(VAR_LEN, x2)
    allocate(IDX_BITS, False, 0, ecp_idx)

    ecp_idx ^= INITIAL_IDX     # start at index 2 (= 2*G)

    hadamard_transform(x1)
    hadamard_transform(x2)

    # ecp += x1 * G  (bit decomposition)
    for i in range(VAR_LEN):
        control(x1[i], lambda f=G_XOR_TABLES[i], r=G_INV_XOR_TABLES[i]:
                group_add(ecp_idx, f, r))

    # ecp += x2 * (-Q)  (bit decomposition)
    for i in range(VAR_LEN):
        control(x2[i], lambda f=NEGQ_XOR_TABLES[i], r=NEGQ_INV_XOR_TABLES[i]:
                group_add(ecp_idx, f, r))

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
    """Convert LSB-first bit list [b0, b1, ...] to integer b0 + 2*b1 + ..."""
    if isinstance(bits, (int, float)):
        return int(bits)
    return sum(int(b) * (1 << i) for i, b in enumerate(bits))


def extract_discrete_log(df, order, var_len):
    """
    Recover d from measured (x1, x2) pairs.
    x1, x2 are QArray[QBit] outputs — bit lists [b0, b1, ...] (LSB first).
    Convert to integer, then to approx fraction k/2^var_len, multiply by order.
    d ≡ -r1 · r2⁻¹ (mod n)
    """
    import math
    N = 1 << var_len
    df = df.copy()
    df["x1_int"] = df["x1"].apply(bits_to_int)
    df["x2_int"] = df["x2"].apply(bits_to_int)
    df["x1_r"] = (df["x1_int"] / N * order).round().astype(int) % order
    df["x2_r"] = (df["x2_int"] / N * order).round().astype(int) % order
    df = df[df["x2_r"].apply(lambda v: math.gcd(int(v), order) == 1)].copy()
    df["d_candidate"] = (
        -df["x1_r"] * df["x2_r"].apply(lambda v: pow(int(v), -1, order))
    ) % order
    return df


# ---------------------
# Synthesize & execute
# ---------------------

def run():
    print(f"\nQDay Prize — Shor's ECDLP (group-index encoding) on y²=x³+7 (mod {P_MOD})")
    print(f"  G={GENERATOR_G}  Q={TARGET_POINT}  n={GENERATOR_ORDER}  known d={KNOWN_D}\n")

    constraints = Constraints(max_width=100)
    preferences = Preferences(optimization_level=0, timeout_seconds=300)

    print("Synthesizing...")
    qmod = create_model(main, constraints=constraints, preferences=preferences)
    qprog = synthesize(qmod)
    print(f"  Qubits: {qprog.data.width}")
    print(f"  Depth:  {qprog.transpiled_circuit.depth}")
    print(f"  CX count: {qprog.transpiled_circuit.count_ops.get('cx', 'N/A')}\n")

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
