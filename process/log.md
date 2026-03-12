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
