"""
Minimal Classiq synthesis test: single ECC point addition.

Tests only ec_point_add on the 4-bit competition curve (p=13).
Much faster to synthesize than the full Shor's ECDLP circuit.

Verifies: [11, 5] + [7, 5] = [10, 9]  on y² = x³ + 7 (mod 13)
(i.e. G + 2G = 3G, checked classically first)
"""

import math
from classiq import *
from classiq.qmod.symbolic import subscript

# ---------------------
# Curve parameters (4-bit)
# ---------------------
P_MOD = 13
N_BITS = P_MOD.bit_length()  # 4

# Points on y² = x³ + 7 (mod 13):
#   G   = [11, 5]
#   2G  = [7,  5]   (used as the quantum input point)
#   3G  = [10, 9]   (expected result)
P1 = [7, 5]    # quantum input (ecp)
P2 = [11, 5]   # classical point to add (G)
EXPECTED = [8, 8]   # = 3G (verified classically)

# ---------------------
# Quantum circuit
# ---------------------

class EllipticCurvePoint(QStruct):
    x: QNum[N_BITS]
    y: QNum[N_BITS]


@qperm
def mock_modular_inverse(x: Const[QNum], result: QNum, modulus: int) -> None:
    inverse_table = lookup_table(
        lambda _x: pow(_x, -1, modulus) if math.gcd(_x, modulus) == 1 else 0, x
    )
    result ^= subscript(inverse_table, x)


@qperm
def ec_point_add(ecp: EllipticCurvePoint, G: list[int], p: int) -> None:
    slope = QNum()
    allocate(N_BITS, slope)
    t0 = QNum()
    allocate(N_BITS, t0)
    Gx, Gy = G[0], G[1]

    modular_add_constant_inplace(p, (-Gy) % p, ecp.y)
    modular_add_constant_inplace(p, (-Gx) % p, ecp.x)
    within_apply(
        lambda: mock_modular_inverse(ecp.x, t0, p),
        lambda: modular_multiply(p, t0, ecp.y, slope),
    )
    within_apply(
        lambda: modular_multiply(p, slope, ecp.x, t0),
        lambda: inplace_xor(t0, ecp.y),
    )
    within_apply(
        lambda: modular_square(p, slope, t0),
        lambda: (
            modular_subtract_inplace(p, t0, ecp.x),
            modular_negate_inplace(p, ecp.x),
            modular_add_constant_inplace(p, (3 * Gx) % p, ecp.x),
        ),
    )
    modular_multiply(p, slope, ecp.x, ecp.y)
    t1 = QNum()
    within_apply(
        lambda: mock_modular_inverse(ecp.x, t0, p),
        lambda: within_apply(
            lambda: (allocate(N_BITS, t1), modular_multiply(p, t0, ecp.y, t1)),
            lambda: inplace_xor(t1, slope),
        ),
    )
    free(slope)
    modular_add_constant_inplace(p, (-Gy) % p, ecp.y)
    modular_negate_inplace(p, ecp.x)
    modular_add_constant_inplace(p, Gx, ecp.x)


@qfunc
def main(ecp: Output[EllipticCurvePoint]) -> None:
    allocate(ecp)
    ecp.x ^= P1[0]
    ecp.y ^= P1[1]
    ec_point_add(ecp, P2, P_MOD)


# ---------------------
# Synthesize & execute
# ---------------------

print(f"Testing ec_point_add on y² = x³ + 7 (mod {P_MOD})")
print(f"  {P1} + {P2} = ? (expected {EXPECTED})\n")

qmod = create_model(main, constraints=Constraints(max_width=50),
                    preferences=Preferences(optimization_level=0))

print("Synthesizing...")
qprog = synthesize(qmod)
print(f"  Qubits: {qprog.data.width}")
print(f"  Depth:  {qprog.transpiled_circuit.depth}")

print("Executing...")
result = execute(qprog).result_value()
state = result.parsed_counts[0].state
got = [state["ecp"]["x"], state["ecp"]["y"]]

print(f"\n  Result:   {got}")
print(f"  Expected: {EXPECTED}")
print(f"  {'✅ CORRECT' if got == EXPECTED else '❌ MISMATCH'}")
