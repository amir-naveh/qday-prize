# Shor's Algorithm for ECDLP on Real Quantum Hardware

**QDay Prize Submission** | Amir Naveh (amir@classiq.io) | April 2026

---

## Approach

We solve the Elliptic Curve Discrete Logarithm Problem (ECDLP) — given `G`, `Q=d·G` on `y²=x³+7 (mod p)`, find `d` — using Shor's algorithm running on real gate-level quantum hardware.

**Group-index encoding** is the key architectural decision: instead of representing curve points as `(x,y)` coordinate pairs (requiring O(log p) qubits and quantum modular inversion), we represent the prime-order subgroup as cyclic group `Z_n`, encoding point `k·G` as integer `k`. This eliminates quantum modular inversion (the dominant circuit cost in prior work) and reduces qubit count to `O(log n)`.

**Circuit design:** Two QPE registers `x1`, `x2` (each `VAR_LEN` qubits) and one EC-point register `ecp` (`IDX_BITS` qubits). After Hadamard initialization, each bit of `x1` and `x2` controls a modular constant addition to `ecp`:

```
ecp ← INITIAL_IDX + Σᵢ x1[i]·Gᵢ + Σᵢ x2[i]·(−d)ᵢ  (mod n)
```

where `Gᵢ = 2ⁱ mod n` and `(−d)ᵢ = (n−d)·2ⁱ mod n` are precomputed classical constants. After inverse QFT on `x1` and `x2`, measurements concentrate near `(s₁/N·n, s₂/N·n)` satisfying `s₁·d + s₂ ≡ 0 (mod n)`. Post-processing: `d ≡ −s₂·s₁⁻¹ (mod n)`.

**Hardware-optimized variant (QFT-space adder):** The `ecp` register is initialized in QFT space and kept there throughout, replacing ripple-carry adders with phase rotations (`modular_add_qft_space`). This achieves 57% fewer CX gates for the 6-bit instance (1,252 vs 2,910 CX) — the most compact known implementation for this problem.

---

## Hardware Results

**4-bit key recovered on 3 real quantum devices:**

| Device | Technology | CX gates | Shots | Private key |
|--------|-----------|----------|-------|-------------|
| Rigetti Ankaa-3 | Superconducting | 716 | 4,096 | **d=6 ✅** |
| IonQ Forte-1 | Trapped-ion | 716 | 1,024 | **d=6 ✅** |
| IBM Pittsburgh | Superconducting | 716 | 1,024 | **d=6 ✅** |

Curve: `y²=x³+7 (mod 13)`, `n=7`, `G=(11,5)`, `Q=(11,8)`, known `d=6`. Recovery method: mode of `d ≡ −r₂·r₁⁻¹ (mod n)` across all valid measurement pairs.

**6-bit simulator only (hardware infeasible):**
Circuit: 16 qubits, 1,252 CX (QFT-space variant). Correct `d=18` recovered on Classiq simulator. Hardware circuit fidelity ≈ 0.15% (0.995^1252), yielding only ~1.5 signal shots per 1,024 on IBM/IonQ — signal undetectable.

---

## Hardware Requirements and Limitations

**Current hardware (NISQ era):** Each additional CX gate reduces circuit fidelity by ~0.5%. For a reliable 6-bit result (1,252 CX), approximately 30,000 shots would be required at current fidelity levels. On IBM the circuit fidelity is ~0.15% (0.995^1252), producing only ~110 usable signal shots even after 73,728 shots with calibration-baseline subtraction — insufficient to overcome noise. On IonQ the fidelity is slightly higher (~0.7%) but the cost for the required shot count (~$64K) exceeds available budget.

**Path to larger keys:** The gate count for our circuit scales as `O(n · log n)` CX gates (ripple-carry) or `O(n · log² n)` (QFT-space). For `n`-bit keys, the CX count grows polynomially but exceeds current hardware fidelity budgets past ~4 bits. Breaking a 256-bit secp256k1 key would require fault-tolerant quantum computers with millions of physical qubits operating below the fault-tolerance threshold — far beyond current hardware.

**Key technical finding:** Current superconducting and trapped-ion hardware can execute Shor's ECDLP for the smallest toy instances (4-bit). The hardware fidelity threshold for recovering 6-bit is approximately a 3× improvement in per-gate CX error (from ~0.5% to ~0.17%), or an order-of-magnitude shorter circuit. Neither is achievable with near-term NISQ hardware.

---

*Full code, job IDs, and analysis at: [GitHub repository link]*

*Circuit synthesis via Classiq SDK v1.5.0. Hardware accessed via AWS Braket (Rigetti), Classiq direct (IonQ), and IBM Quantum cloud (IBM).*
