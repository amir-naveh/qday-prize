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
