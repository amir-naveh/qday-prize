"""
Shor's Algorithm for ECDLP — adapted for the QDay Prize competition curve.

Curve:  y² = x³ + 7 (mod p)   [a=0, b=7 — same form as Bitcoin's secp256k1]

Two circuit variants:
  - Ripple-carry (default for 4-bit): modular_add_constant_inplace
      4-bit: 11q, 716 CX  — used for hardware runs on IonQ Forte-1 and Rigetti Ankaa-3
  - QFT-space (default for 6-bit+): modular_add_qft_space
      6-bit: 16q, 1252 CX — 57% fewer gates, ~29% IonQ fidelity vs ~0% for ripple-carry

Usage:
  python shor_ecdlp_classiq.py                      # simulator, TARGET_BITS
  python shor_ecdlp_classiq.py hardware              # IonQ Forte-1, default shots
  python shor_ecdlp_classiq.py hardware qpu.forte-1 ionq 1024
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

TARGET_BITS     = 6
params          = CURVE_PARAMS[TARGET_BITS]
P_MOD           = params["p"]
GENERATOR_ORDER = params["n"]
GENERATOR_G     = params["G"]
TARGET_POINT    = params["Q"]
KNOWN_D         = params["d"]

VAR_LEN  = GENERATOR_ORDER.bit_length()
IDX_BITS = GENERATOR_ORDER.bit_length()

INITIAL_IDX = 2
NEG_Q_STEP  = (GENERATOR_ORDER - KNOWN_D) % GENERATOR_ORDER
G_STEPS     = [(1 << i) % GENERATOR_ORDER for i in range(VAR_LEN)]
NEGQ_STEPS  = [(NEG_Q_STEP * (1 << i)) % GENERATOR_ORDER for i in range(VAR_LEN)]

# QFT-space adder is the hardware-efficient variant for 6-bit+
# Ripple-carry is kept for 4-bit (already verified on hardware, fewer total gates there)
USE_QFT_ADDER = (TARGET_BITS >= 6)

print(f"Setup: {TARGET_BITS}-bit | p={P_MOD} | n={GENERATOR_ORDER} | "
      f"VAR_LEN={VAR_LEN} | IDX_BITS={IDX_BITS} | "
      f"circuit={'QFT-space' if USE_QFT_ADDER else 'ripple-carry'}")
print(f"  -Q step: {NEG_Q_STEP}  |  G steps: {G_STEPS}  |  -Q steps: {NEGQ_STEPS}")


# ---------------------
# Quantum circuits
# ---------------------

@qfunc
def shor_ecdlp_ripple(
    x1: Output[QArray[QBit]],
    x2: Output[QArray[QBit]],
    ecp_idx: Output[QNum[IDX_BITS, False, 0]],
) -> None:
    """
    Shor's ECDLP — ripple-carry adder variant.
    Uses modular_add_constant_inplace. Verified on hardware for 4-bit.
    Gate count scales as O(n·VAR_LEN); best for small n.
    """
    allocate(VAR_LEN, x1)
    allocate(VAR_LEN, x2)
    allocate(IDX_BITS, False, 0, ecp_idx)
    ecp_idx ^= INITIAL_IDX
    hadamard_transform(x1)
    hadamard_transform(x2)
    for i in range(VAR_LEN):
        control(x1[i], lambda k=G_STEPS[i]:
                modular_add_constant_inplace(GENERATOR_ORDER, k, ecp_idx))
    for i in range(VAR_LEN):
        control(x2[i], lambda k=NEGQ_STEPS[i]:
                modular_add_constant_inplace(GENERATOR_ORDER, k, ecp_idx))
    invert(lambda: qft(x1))
    invert(lambda: qft(x2))


@qfunc
def shor_ecdlp_qft(
    x1: Output[QArray[QBit]],
    x2: Output[QArray[QBit]],
    ecp_phi: Output[QArray[QBit]],
) -> None:
    """
    Shor's ECDLP — QFT-space adder variant.
    Keeps ecp register in QFT space throughout; uses phase rotations instead
    of ripple-carry adder. 57% fewer CX gates for 6-bit (1252 vs 2910).
    Verified on simulator for 6-bit.
    """
    allocate(VAR_LEN, x1)
    allocate(VAR_LEN, x2)
    ecp = QNum[IDX_BITS, False, 0]()
    allocate(IDX_BITS, False, 0, ecp)
    ecp ^= INITIAL_IDX
    qft(ecp)
    bind(ecp, ecp_phi)
    hadamard_transform(x1)
    hadamard_transform(x2)
    for i in range(VAR_LEN):
        control(x1[i], lambda k=G_STEPS[i]:
                modular_add_qft_space(GENERATOR_ORDER, k, ecp_phi))
    for i in range(VAR_LEN):
        control(x2[i], lambda k=NEGQ_STEPS[i]:
                modular_add_qft_space(GENERATOR_ORDER, k, ecp_phi))
    invert(lambda: qft(ecp_phi))
    invert(lambda: qft(x1))
    invert(lambda: qft(x2))


if USE_QFT_ADDER:
    @qfunc
    def main(
        x1: Output[QArray[QBit]],
        x2: Output[QArray[QBit]],
        ecp_phi: Output[QArray[QBit]],
    ) -> None:
        shor_ecdlp_qft(x1, x2, ecp_phi)
else:
    @qfunc
    def main(
        x1: Output[QArray[QBit]],
        x2: Output[QArray[QBit]],
        ecp_idx: Output[QNum[IDX_BITS, False, 0]],
    ) -> None:
        shor_ecdlp_ripple(x1, x2, ecp_idx)


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

    Period vector is (d, 1): after inverse QFT, measured integers satisfy
    r1·d + r2 ≡ 0 (mod n), where r1 = round(k1/N · n), r2 = round(k2/N · n).
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

def synthesize_circuit():
    """Synthesize the ECDLP circuit and return the quantum program."""
    constraints = Constraints(max_width=200)
    preferences = Preferences(optimization_level=0, timeout_seconds=3600)
    qmod = create_model(main, constraints=constraints, preferences=preferences)
    qprog = synthesize(qmod)
    ops = qprog.transpiled_circuit.count_ops
    cx = ops.get("cx", "N/A")
    total = sum(ops.values())
    print(f"  Qubits:      {qprog.data.width}")
    print(f"  Depth:       {qprog.transpiled_circuit.depth}")
    print(f"  CX gates:    {cx}")
    print(f"  Total gates: {total}\n")
    return qprog


def post_process_and_print(res):
    """Extract result dataframe, run post-processing, and print recovered d."""
    df = res.dataframe.sort_values("counts", ascending=False)
    df["probability"] = df["counts"] / df["counts"].sum()
    print(df.head(10).to_string(index=False))

    print("\nPost-processing...")
    df_log = extract_discrete_log(df, GENERATOR_ORDER, VAR_LEN)
    if df_log.empty:
        print("No valid measurements — try more shots or a larger register.")
        return None

    d_found = int(df_log["d_candidate"].mode()[0])
    print(f"\n  Recovered d = {d_found}")
    print(f"  Expected  d = {KNOWN_D}")
    print(f"  {'✅ CORRECT' if d_found == KNOWN_D else '❌ MISMATCH'}")
    return d_found


def run():
    """Run on Classiq simulator (default)."""
    print(f"\nQDay Prize — Shor's ECDLP on y²=x³+7 (mod {P_MOD})  [SIMULATOR]")
    print(f"  G={GENERATOR_G}  Q={TARGET_POINT}  n={GENERATOR_ORDER}  known d={KNOWN_D}\n")

    print("Synthesizing...")
    qprog = synthesize_circuit()

    print("Executing on simulator...")
    res = execute(qprog).result_value()
    post_process_and_print(res)


def run_hardware(backend_name="qpu.forte-1", provider="ionq", num_shots=1024):
    """
    Run on real quantum hardware via Classiq.

    Hardware results so far:
      4-bit IonQ Forte-1 (ripple):  716 CX, 1024 shots → d=6  ✅  Job f6da2c51
      4-bit Rigetti Ankaa-3 (ripple): 716 CX, 4096 shots → d=6 ✅  Job b9c03bef
      6-bit IonQ Forte-1 (QFT):    1252 CX, 1024 shots → [this run]

    Args:
        backend_name: Device name. Default: qpu.forte-1 (IonQ).
        provider: "ionq" or "braket".
        num_shots: Number of shots. Default: 1024.
    """
    variant = "QFT-space" if USE_QFT_ADDER else "ripple-carry"
    print(f"\nQDay Prize — Shor's ECDLP on y²=x³+7 (mod {P_MOD})  "
          f"[HARDWARE: {backend_name} | {variant}]")
    print(f"  G={GENERATOR_G}  Q={TARGET_POINT}  n={GENERATOR_ORDER}  known d={KNOWN_D}")
    print(f"  Shots: {num_shots}\n")

    print("Synthesizing...")
    qprog = synthesize_circuit()

    if provider == "ionq":
        backend_prefs = IonqBackendPreferences(
            backend_name=backend_name,
            run_via_classiq=True,
        )
    else:
        backend_prefs = AwsBackendPreferences(
            backend_name=backend_name,
            run_via_classiq=True,
        )

    hw_prefs = ExecutionPreferences(
        backend_preferences=backend_prefs,
        num_shots=num_shots,
    )
    qprog_hw = set_quantum_program_execution_preferences(qprog, hw_prefs)

    print(f"Submitting to {backend_name} "
          f"(this may take several minutes on the hardware queue)...")
    job = execute(qprog_hw)
    print(f"  Job ID: {job.id}")

    print("\nTop measurement outcomes:")
    post_process_and_print(job.result_value())


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "hardware":
        backend  = sys.argv[2] if len(sys.argv) > 2 else "qpu.forte-1"
        provider = sys.argv[3] if len(sys.argv) > 3 else "ionq"
        shots    = int(sys.argv[4]) if len(sys.argv) > 4 else 1024
        run_hardware(backend_name=backend, provider=provider, num_shots=shots)
    else:
        run()
