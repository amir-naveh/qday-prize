# SteveTipp / Qwork — QDay Prize Competitor Analysis

*Source: https://github.com/SteveTipp/Qwork.github.io*
*arXiv: https://arxiv.org/abs/2507.10592*
*Last updated: 2026-03-19*

---

## Submission Summary

- **Author:** Steve Tippeconnic (ASU cybersecurity student, stippeco@asu.edu)
- **Claimed key size:** 6-bit (Experiment 76, submitted to QDay Prize)
- **Published paper:** 5-bit result on arXiv (2507.10592, Jul 2025)
- **Hardware:** IBM ibm_torino (133-qubit Heron r2), Qiskit Runtime 2.0

---

## Circuit Architecture

Different approach from ours:
- **No Classiq SDK** — hand-written Qiskit circuits
- Uses ancilla qubits: 5-bit run = 10 logical + 5 ancilla = 15 qubits; 6-bit = 12 logical + 6 ancilla = 18 qubits
- **Transpiled to ibm_torino native gates** (sx, cz, rz, x — Heron r2 basis uses CZ not CX)

### 5-bit circuit (arXiv paper, Experiment 73)

| Parameter | Value |
|-----------|-------|
| Hardware | ibm_torino |
| Physical qubits | 15 |
| Circuit depth | **67,428** |
| CZ gates | **34,319** |
| Shots | 16,384 |
| Date | 2025-06-25 |

### 6-bit circuit (QDay submission, Experiment 76)

| Parameter | Value |
|-----------|-------|
| Hardware | ibm_torino |
| Physical qubits | 18 |
| Circuit depth | not published |
| CZ gates | not published |
| Shots | 16,384 |

---

## Statistical Assessment — Critical Findings

### 5-bit result

The arXiv abstract claims k=7 "found in top 100 results" — **this is technically true but misleading:**

- k=7 raw count: 54/16,384 shots (rank ~4 among invertible pairs)
- Highest count was k=8 (count=63), k=7 was NOT the top result
- With best post-processing (toroidal smoothing + weighted exact-line scoring): k=7 reaches **rank 3**, still not rank 1
- Bootstrap robustness (500 replicates): **k=7 wins rank-1 in 0/500 replicates** (0%); k=0 wins 500/500
- From their own analysis file (`FIVE_BIT_INTERFERENCE_ANALYSIS_NOTE.md`): `true_k_rank_1_rate = 0.0`

### 6-bit result

The QDay submission claims 6-bit broken — **similarly weak:**

- After 10+ stages of tuned post-processing (Method 6): k=42 reaches **rank 3**, best_k = 40 (wrong)
- Bootstrap: **k=42 wins rank-1 in 0/500 replicates**; k=40 wins 182/500
- Top-3 rate: 14.2% — highly unstable
- Their own conclusion: "does not achieve robust direct recovery of the true key as the top-ranked candidate"

---

## Comparison vs. Our Submission

| Dimension | SteveTipp | Ours |
|-----------|-----------|------|
| Claimed key size | 6-bit | 4-bit |
| Hardware | IBM ibm_torino | Rigetti Ankaa-3, IonQ Forte-1, IBM Pittsburgh |
| Devices | 1 | 3 |
| CZ/CX gates (5-bit) | 34,319 CZ | — |
| CX gates (4-bit) | — | 716 CX |
| Circuit depth (5-bit) | 67,428 | — |
| Key recovery (rank-1 rate) | **0%** in bootstrap | Mode of shots (robust) |
| Post-processing | 10+ engineered stages to reach rank 3 | Simple: mode of `(-r2·r1⁻¹) mod n` |
| Classical verification | Not direct top-1 | d=6 is direct top-1 result on all 3 devices |
| arXiv paper | Yes (5-bit, Jul 2025) | No |

---

## Circuit Depth Comparison

Their 5-bit circuit has **34,319 CZ gates** and depth **67,428** on ibm_torino.

ibm_torino CZ fidelity ≈ 99.5% → circuit fidelity = 0.995^34,319 ≈ **1.4 × 10⁻⁷⁵**

This is essentially zero. The circuit is entirely noise — what they observe is a flat noise floor, and the signal they claim to "recover" is extracted via an elaborate post-processing pipeline tuned to the known answer. Their own bootstrap confirms the result is not reproducible.

By contrast, our 4-bit result uses 716 CX gates → fidelity ≈ 0.995^716 ≈ 2.8% — sufficient signal for direct top-1 recovery.

---

## Conclusion

SteveTipp's submission is **statistically invalid**: the true k is never the top-ranked result even with heavily engineered post-processing, and the result is bootstrapped to 0% top-1 rate. The circuit depth (67K layers, 34K CZ gates) implies near-zero circuit fidelity — the measurement outcomes are dominated by noise, and the "signal" is post-hoc curve-fitting.

Our 4-bit result on 3 devices with 716 CX gates is a **stronger and more reproducible quantum result**, even at a smaller key size.
