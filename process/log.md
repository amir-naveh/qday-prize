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
