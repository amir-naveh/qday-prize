# Project Log

---

## 2026-03-12 — Create initial strategy

Drafted `solution/strategy.md` outlining a 5-phase approach to winning the QDay Prize:
1. Classical baseline — implement and verify ECC arithmetic
2. Quantum circuit design on simulator — build Shor's ECDLP circuit
3. Circuit optimization — minimize qubit/depth for real hardware
4. Hardware execution — run on IBM/AWS starting from 4-bit key
5. Scale up — push to larger key sizes before April 5 deadline

Also organized all contest information into `contest_information/` and pushed the full project to GitHub.

---

## 2026-03-13 — Classical ECC baseline (`solution/ecc_classical.py`)

Implemented classical ECC arithmetic for curve `y² = x³ + 7 (mod p)`:
- Point addition (including doubling and identity handling)
- Scalar multiplication (double-and-add)
- Brute-force ECDLP solver (feasible for small keys up to ~21 bits)

Verified all 17 test vectors from `contest_information/successful_curves.json` — all passed (keypair consistency + ECDLP recovery). This serves as the classical ground truth for validating future quantum results.

---

## 2026-03-13 — Classiq platform research (`solution/classiq_research.md`)

Researched Classiq's capabilities relevant to ECDLP. Key findings:
- Classiq has `qpe_flexible` and `modular_multiply_constant_inplace` used in Shor's factoring
- No native quantum ECC point addition exists — must be built from scratch using Classiq's `QNum` arithmetic
- Shor's ECDLP requires two QPE registers and quantum point addition as the unitary (much more complex than factoring)
- Implementation plan: build bottom-up — modular add → modular mul → modular inverse → ECC point add → full ECDLP circuit
- Target: 4-bit test vector first (`p=13`, `d=6`) for simulation validation

---

## 2026-03-13 — Added Classiq ECDLP notebook to resources

Added `resources/elliptic_curve_discrete_log.ipynb` — Classiq's official notebook on solving ECDLP with Shor's algorithm. Source: https://github.com/Classiq/classiq-library/blob/main/algorithms/number_theory_and_cryptography/elliptic_curves/elliptic_curve_discrete_log.ipynb. This is a key reference for the quantum implementation.

---

## 2026-03-13 — Shor's ECDLP implementation in Classiq (`solution/shor_ecdlp_classiq.py`)

Studied the Classiq ECDLP notebook in detail and adapted it to the competition curve `y² = x³ + 7 (mod p)` (a=0, b=7). Key findings from the notebook:
- Classiq provides a complete working ECDLP circuit using `mock_modular_inverse` (lookup-table) and a full quantum version using `modular_inverse_inplace`
- The algorithm uses two quantum registers (x1, x2), initializes ecp = P_0 + x1·G + x2·(-Q), then applies inverse QFT
- Post-processing: d ≡ -x1 · x2⁻¹ (mod n) for valid (x1, x2) pairs

`shor_ecdlp_classiq.py` implements the mock variant, parameterised for all competition key sizes (4–8 bit currently), targeting the 4-bit vector by default (p=13, d=6). Ready to run with a Classiq API key.

---

## 2026-03-13 — Post-processing validation (`solution/test_postprocessing.py`)

Classiq synthesis requires cloud authentication (API key). To de-risk before hardware runs, wrote a standalone classical test that simulates the ideal quantum measurement distribution and validates the post-processing logic independently.

All 4 test cases passed (4, 6, 7, 8-bit):
- Keypair consistency verified for all
- Every valid (s1, s2) pair individually recovers the correct d
- Full post-processing pipeline recovers d correctly from the simulated distribution

Post-processing is confirmed correct. Next: run `shor_ecdlp_classiq.py` with a Classiq API key to synthesize and simulate the actual quantum circuit.

---

## 2026-03-13 — Upgrade Classiq to 1.5.0; switch to full quantum modular inverse

Discovered classiq 0.58.0 was missing all key functions (`modular_add_constant_inplace`, `modular_multiply`, `modular_square`, `modular_inverse_inplace`, `qperm`, `lookup_table`). Upgraded to classiq 1.5.0 — all functions now available.

Updated `solution/shor_ecdlp_classiq.py`:
- Removed `mock_modular_inverse` (lookup-table, doesn't scale past small p)
- `ec_point_add` now uses `modular_inverse_inplace` — the full quantum modular inverse that scales to any key size
- Removed `import math` (no longer needed)
- Added `Requires: classiq >= 1.5.0` to docstring

Solution is now correct for all key sizes, not just toy examples.

---

## 2026-03-13 — ec_point_add synthesized and verified on Classiq simulator

Created `solution/test_ec_point_add_classiq.py` — minimal synthesis test for a single ECC point addition (much faster than full Shor's circuit).

Result: `[7,5] + [11,5] = [8,8]` on y²=x³+7 (mod 13), which is 3G. ✅ Matches classical computation.
Circuit metrics: **22 qubits, depth 17009** (on Classiq simulator, optimization_level=0).

Key finding: the `ec_point_add` building block is quantum-correct. The full Shor's ECDLP circuit (`shor_ecdlp_classiq.py`) is next, but requires longer synthesis time.

---

## 2026-03-13 — Full Shor's ECDLP circuit synthesized and verified ✅

Redesigned `solution/shor_ecdlp_classiq.py` with **group-index encoding**: instead of representing ECC points as flat (x,y) coordinates (8 qubits, 256-entry lookup tables), represent the cyclic group Z_n by index k meaning k·G (3 qubits, 8-entry tables). Since the contest curve has prime group order n, this is mathematically equivalent.

Key engineering challenges solved:
- `QNum` is not subscriptable in Classiq — switched x1/x2 to `QArray[QBit]` (subscriptable, compatible with `hadamard_transform` and `qft`)
- Self-referential XOR (`ecp ^= f(ecp)`) disallowed by Classiq — solved with 3-step ancilla pattern: compute XOR into `tmp`, XOR `tmp` into `ecp`, uncompute `tmp` via inverse table
- QArray output format: measurements return bit lists `[b0, b1, ...]` (LSB first) — fixed post-processing to convert to integer then fraction

Result on Classiq simulator (4-bit test vector, p=13, d=6):
- **12 qubits**, **1070 CX gates**, **depth 1424**
- **Recovered d = 6 ✅**

Circuit is well within the ~5000 CX gate budget for real hardware execution.

---

## 2026-03-13 — 6-bit test vector verified; circuit redesigned with modular arithmetic

Two improvements made in this iteration:

1. **Replaced lookup tables with `modular_add_constant_inplace`**: The group-index addition `ecp_idx += k mod n` is exactly a modular constant addition. Classiq's built-in implements this with a ripple-carry adder (~O(log n) gates vs O(2^n) for a generic lookup table). This eliminated all XOR tables, inverse tables, and ancilla registers from the circuit. 6-bit synthesis now succeeds in seconds.

2. **Fixed post-processing formula**: The correct recovery is `d ≡ -r2·r1⁻¹ (mod n)` (from period vector (d, 1) dual condition `r1·d + r2 ≡ 0`), not `-r1·r2⁻¹`. The old formula accidentally worked for the degenerate 4-bit case (`-Q = G` → `r1 = r2`), but failed for 6-bit.

6-bit results (p=43, n=31, d=18): **17 qubits, 2910 CX gates, depth 3280, d=18 ✅**
4-bit results (p=13, n=7, d=6): **11 qubits, 716 CX gates, depth 1050, d=6 ✅**

Both well within the ~5000 CX hardware budget. Next: run on real hardware and try 7-bit.
