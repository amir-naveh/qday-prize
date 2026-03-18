# GitHub Repo: SteveTipp/Qwork.github.io — Full Fetched Content

Source: https://github.com/SteveTipp/Qwork.github.io
Website: https://www.qubits.work (redirects to https://stevetipp.github.io/Qwork.github.io/)

---

## README.md (verbatim)

```
Qwork

Author: Steve Tippeconnic (stippeco@asu.edu)
License: MIT
Website: https://www.qubits.work

Qwork is an open-source research project exploring quantum computation using IBM's superconducting quantum computers.
Each experiment hosted here is executed on real IBM Quantum backends and released with its full JSON backend data, circuit source, and visualization code for reproducibility.

The data in this public repo is rendered at https://www.qubits.work.

Thank you!
```

---

## P11_QDAY_README.md (verbatim)

```
QDay Prize Info
Email: Stippeco@asu.edu
Background: ASU Cybersecurity graduate working on IBM's quantum systems for two years.
Length of Key submitted: 6-bit
Model: IBM Torino - full backend specs are in the PDF.
To run: Copy code from PDF, enter your backend CRN and API Key, and then run.
```

---

## Repository Statistics

- 1,695 commits on main branch
- 12 stars
- 4 forks
- 3 watchers
- 670+ files

---

## FIVE_BIT_INTERFERENCE_ANALYSIS_NOTE.md (verbatim)

### 1) Corrected Bitstring-to-(a,b) Mapping

Data source is fixed: `data/Shors_ECC_5_Bit_Key_0.json`.

Current `prepare.py` mapping:
- Split each 10-bit key into two 5-bit halves: `left = bits[:5]`, `right = bits[5:]`.
- **Swap halves**.
- **Do not reverse** bit order inside either half.
- Convert directly: `a = int(right, 2)`, `b = int(left, 2)`.

This mapping is used to build `runs/prepared_result.json`.

### 2) Progression of Analysis Improvements

All stages use ridge family `a + k b ≡ 0 (mod 32)`, `k ∈ {0,...,31}`, evaluated at `true_k = 7`.

| Stage | Method change | best_k | true_rank | gap(true - best_false) | z_separation_true_k |
|---|---|---:|---:|---:|---:|
| Raw baseline | Original mapping + exact-line sum | 0 | 26 | -0.03875732421875 | -0.49891186462154014 |
| Corrected mapping baseline | Swap halves, no reversal + exact-line sum | 0 | 8 | -0.01361083984375 | 0.23917497180906144 |
| Toroidal smoothing | Add toroidal 3x3 box smoothing before scoring | 0 | 3 | -0.006083170572916664 | 0.6385353502668066 |
| Weighted exact-line scoring (final) | Keep exact ridge; score `sum p(a,b)^2` on ridge | 0 | 3 | -0.000012662077759519034 | 1.0331175218810753 |

### 3) Final Single-Run Metrics

From `runs/latest_analysis.json`:
- `best_k = 0`
- `true_rank = 3`
- `score_gap_true_minus_best_false = -1.2662077759519034e-05`
- `z_separation_true_k = 1.0331175218810753`

### 4) Bootstrap Robustness Metrics

Bootstrap configuration:
- Replicates: `500`
- Seed: `12345`
- Resample from observed grid distribution, then rerun the **same** smoothing + weighted exact-line pipeline.

Results:
- `true_k_rank_1_rate = 0.0`
- `true_k_top_3_rate = 0.472`
- `true_k_top_5_rate = 0.806`
- `true_rank_mean = 4.114`
- `true_rank_std = 1.581456290891405`
- `z_separation_true_k_mean = 1.033128547005442`
- `z_separation_true_k_std = 0.241619411969828`

### 5) Dominant False-Candidate Findings

Across bootstrap replicates:
- Rank-1 winner frequency: `k=0` wins `500/500` (`1.0`).
- Most frequent candidates above `k=7`: `[0, 16, 14, 21, 31]`.
- Average gap to top false across bootstrap:
  - `avg_score_gap_true_minus_top_false = -1.2413845753964083e-05`
- Competition pattern is **dominated**, not diffuse.

### 6) Geometric Competitor Interpretation

Competitors analyzed: `k = 0, 16, 14, 21, 31`.

- Ridge overlap with `k=7` is generally low:
  - `k=0: 0.03125`, `k=16: 0.03125`, `k=14: 0.03125`, `k=21: 0.0625`, `k=31: 0.25`.
- Ridge-intensity correlation with `k=7` (on smoothed grid, scored intensities) is low:
  - `k=0: 0.0139`, `k=16: 0.0208`, `k=14: 0.0200`, `k=21: 0.0402`, `k=31: 0.0596`.
- Dominance of `k=0` and `k=16` is best explained by:
  - **global marginal bias** (they are top-ranked by marginally expected ridge mass),
  - plus **concentration on a few especially strong ridge points**,
  - rather than substantial geometric overlap with the true ridge.

### Reproducibility

```bash
uv run python prepare.py
uv run python analyze.py
cat runs/latest_analysis.json
```

---

## SIX_BIT_INTERFERENCE_ANALYSIS_NOTE.md (verbatim)

### Fixed Dataset And Target

- Fixed input result: `data/Shors_ECC_6_Bit_Key_0.json`
- Analysis-only workflow: `prepare.py` writes `runs/prepared_result.json`; `analyze.py` writes `runs/latest_analysis.json`
- Modular ridge target: `a + k*b ≡ 0 (mod 64)`
- Fixed constants: `order = 64`, `true_k = 42`

### Mapping Sweep

| Mapping | best_k | true_rank | score_gap_true_minus_best_false | z_separation_true_k |
| --- | ---: | ---: | ---: | ---: |
| `split_left_right_reverse_each_half` | 32 | 28 | -1.0881e-06 | 0.002945 |
| `split_left_right_no_reversal` | 0 | 30 | -1.1426e-06 | -0.173365 |
| `swap_halves_reverse_each_half` | 32 | 32 | -2.9504e-06 | -0.269242 |
| `swap_halves_no_reversal` | 0 | 20 | -3.1261e-06 | -0.044064 |

Recommended mapping: `split_left_right_reverse_each_half`.
Reason: it gave the only positive `z_separation_true_k` and the least-negative true-vs-best-false gap.

### Staged Post-Analysis Tests

All staged tests used the fixed mapping above and the same candidate set `k in {0, ..., 63}`.

| Stage | Description | best_k | true_rank | score_gap_true_minus_best_false | z_separation_true_k |
| --- | --- | ---: | ---: | ---: | ---: |
| 0 | Raw exact-line baseline | 32 | 43 | -4.0894e-03 | -0.342364 |
| 1 | Toroidal `3x3` smoothing + exact-line `sum p(a,b)` | 32 | 30 | -1.8853e-03 | -0.151751 |
| 2 | Toroidal `3x3` smoothing + weighted exact-line `sum p(a,b)^2` | 32 | 28 | -1.0881e-06 | 0.002945 |
| 3 | Thin banded ridge test, modular distance `<= 1` | 32 | 38 | -3.3459e-06 | -0.341296 |
| 4 | Matched-filter exact-ridge overlap test | 32 | 30 | -1.8853e-03 | -0.151751 |
| 5 | Residual symmetry removal for `k=0` and `k=32`, then weighted exact-line scoring | 31 | 32 | -1.2176e-06 | 0.132044 |
| 6 | Fourier / harmonic filtering removing DC and half-modulus components, then weighted exact-line scoring | 47 | 26 | -4.1587e-07 | 0.093137 |
| 7 | Parity-sector analysis, best sector = `even-odd` | 32 | 18 | -7.1618e-07 | 0.977435 |
| 8 | Sparse top-point capped-weight analysis on the `even-odd` sector | 32 | 13 | -5.6997e-07 | 1.013537 |
| 9 | Null-model normalization on the capped-weight `even-odd` sector | 30 | 47 | -9.4955e-01 | -0.060951 |
| 10 | Row-centered positive residual on the capped-weight `even-odd` sector | 40 | 3 | -3.6299e-08 | 1.347784 |

### Parity-Sector Comparison

| Sector | best_k | true_rank | score_gap_true_minus_best_false | z_separation_true_k | top-1 | top-3 | top-5 | true_rank mean | true_rank std | z-sep mean | z-sep std |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `even-even` | 16 | 36 | -6.3275e-07 | -0.087048 | 0.0000 | 0.0000 | 0.0000 | 33.6060 | 12.1352 | -0.0744 | 0.4926 |
| `even-odd` | 32 | 18 | -7.1618e-07 | 0.977435 | 0.0000 | 0.0020 | 0.0160 | 17.4480 | 6.1780 | 0.9705 | 0.1159 |
| `odd-even` | 0 | 43 | 0.0000 | 0.000000 | 0.0000 | 0.0000 | 0.0000 | 43.0000 | 0.0000 | 0.0000 | 0.0000 |
| `odd-odd` | 47 | 54 | -2.9727e-06 | -1.002892 | 0.0000 | 0.0000 | 0.0000 | 54.0000 | 0.0000 | -0.9997 | 0.0028 |

Best-supported parity sector: `even-odd`.

### Current Best Single-Run Metrics (6-bit)

Current best pipeline:
- Fixed mapping: `split_left_right_reverse_each_half`
- Toroidal `3x3` smoothing
- Parity-sector mask: `a` even, `b` odd
- Capped-weight weighted exact-line ridge scoring
- Cap rule: each per-cell ridge contribution uses `min(p(a,b)^2, q_0.90)` within nonzero `even-odd` sector weights
- Row-centered positive residual applied before exact-line scoring

Current best single-run metrics:
- `best_k = 40`
- `true_rank = 3`
- `score_gap_true_minus_best_false = -3.6299e-08`
- `z_separation_true_k = 1.347784`

### Bootstrap Robustness (6-bit, current best pipeline)

- `top-1 rate = 0.0000`
- `top-3 rate = 0.1420`
- `top-5 rate = 0.2460`
- `true_rank mean = 11.4880`
- `true_rank std = 7.3145`
- `z_separation_true_k mean = 1.1788`
- `z_separation_true_k std = 0.3054`

### Dominant False-Candidate Findings (6-bit)

Final Method 6 top candidate states:
- Rank 1: `k = 40`, score `= 2.0367889068618322e-07`
- Rank 2: `k = 30`, score `= 1.9577212551217755e-07`
- Rank 3: `k = 42`, score `= 1.6738035080862451e-07` (true key)

Across bootstrap replicates:
- `k=40: 182/500 (0.364)`, `k=30: 118/500 (0.236)`, `k=38: 43/500 (0.086)`, `k=42: 21/500 (0.042)`, `k=0: 18/500 (0.036)`
- `avg_score_gap_true_minus_top_false = -5.27308227811986e-08`
- Competition pattern is **diffuse**.

### Main Conclusion (6-bit)

The current best-supported 6-bit post-analysis result is Method 6. In this mode, `k = 42` improves substantially: `true_rank` improves to `3`, bootstrap mean rank improves to `11.4880`, bootstrap mean `z_separation_true_k` rises to `1.1788`. However, `best_k` is still not `42`; under Method 6 it is `40`. The ridge-based post-processing family provides a materially stronger signal for `k = 42`, but does not achieve robust direct recovery of the true key as the top-ranked candidate.

---

## Experiment List (from qubits.work)

Experiment 83: Codex Re-Analysis of the Interference Pattern from My IBM Quantum 6-Bit ECC Key Experiment
Experiment 82: Codex Re-Analysis of the Interference Pattern from My 5-Bit ECC Key arXiv Paper
Experiment 81: Recovering a 5-Bit Scalar in an Order-32 Elliptic Curve Subgroup via a Phase-Only Shor-Style Construction (156-Qubits)
Experiment 80: Nonlocal Ridge Encryption via Modular Interference on Two 5-Qubit Registers (156-Qubits)
Experiment 79: Geometric Noise Cancellation of a 5-Bit Quantum arXiv Run via Classical Distribution Subtraction
Experiment 78: Noise Modifications for 'Breaking a 5-Bit Elliptic Curve Key' (133-Qubits)
Experiment 77: Approximating the Speed of Light from 4-bit E=mc² Interference on a 133-Qubit Quantum Computer
Experiment 76: Breaking a 6-Bit Elliptic Curve Key using IBM's 133-Qubit Quantum Computer
Experiment 75: Causal Quantum Timekeeping with Chained Bloch Clocks while Breaking a 3-Bit Elliptic Curve Key via a Shor-style Algorithm
Experiment 74: Quantum Timekeeping while Breaking a 3-Bit Elliptic Curve Key via a Shor-style Algorithm
Experiment 73: Breaking a 5-Bit Elliptic Curve Key
Experiment 72: Breaking a 4-Bit Elliptic Curve Key (133-Qubits)
Experiment 71: Adinkra-Based E8 CSS Code for Quantum Error Detection (133-Qubits)
Experiment 70: Multi-Cavity Topological Casimir Tunneling (133-Qubits)
Experiment 69: Twistor‑Casimir Coupling in a Discrete Null Lattice (100-Qubits)
Experiment 68: Twistor‑Casimir Coupling in a Discrete Null Lattice (49-Qubits)
Experiment 67: Dynamic Casimir Photon Emission (133-Qubits)
Experiment 66: Breaking a 3-Bit Elliptic Curve Key (133-Qubits)
Experiment 65: Topological Chimeric Spinor Projection (127-Qubits)
Experiment 64: Dual‑Diagonal Twistor Surface Code (127-Qubits)
Experiment 63: Twistor-Entangled Quantum Repetition (127-Qubits)
Experiment 62: Twistor-Encoded Error Geometry (127-Qubits)
Experiment 61: Twistor-Encoded Quantum State Stabilization (127-Qubits)
Experiment 60: Twistor-Inspired Quantum Teleportation (127-Qubits)
Experiment 59: Twistor-Inspired Quantum Annealing (127-Qubits)
Experiment 58: Multi-Layer Retrocausal Encryption (127-Qubits)
Experiment 57: Delayed-Choice Entanglement Swapping (127-Qubits)
Experiment 56: Entanglement Dynamics Under the Influence of '(c^4)/G' (127-Qubits)
Experiment 55: Factoring 95 with Shors Algorithm (127-Qubits)
Experiment 54: Factoring 77 with Shor's Algorithm (Simplified) (127-Qubits)
Experiment 53: Exploring State Dynamics in Abstract 1 + 1, 2 + 1, and 3 + 1 Spacetime Dimensions
Experiment 52: Exploring the Geometric Phase of Robinson Congruences in Quantum Circuits (127-Qubits)
Experiment 51: Embedding Clifford Parallels in Multi-qubit Stabilizers (127-Qubits)
Experiment 50: Null-Light Ray Tomography with a Twistor Inspired Circuit (127-Qubits)
Experiment 49: Optimizing Internet Data Packet Routing (127-Qubits)
Experiment 48: Exploring the Traveling Salesman Problem in Non-Euclidean Spaces (127-Qubits)
Experiment 47: Quantum Optimization of Protein Folding Pathways (127-Qubits)
Experiment 46: Quantum Optimization of Neural Network Training Sequences (127-Qubits)
Experiment 45: Drone Delivery Route Optimization (127-Qubits)
Experiment 44: Quantum Algorithm Design for Warehouse Route Optimization (127-Qubits)
Experiment 43: Exploring Plasma Turbulence Using Hierarchical Qubit Clusters (127-Qubits)
Experiment 42: Simulating Quark-Gluon Plasma Interactions (127-Qubits)
Experiment 41: Exploring the Navier-Stokes Equations Using Carleman Linearization (127-Qubits)
Experiment 40: Quantum Field Simulation in Curved Spacetime (127-Qubits)
Experiment 39: Testing the Goldbach Conjecture using Shor's Algorithm (127-Qubits)
Experiment 38: Exploring Prime Factorization Using Shor's Algorithm (127-Qubits)
Experiment 37: Twistor-Inspired Quantum Error Correction (127-Qubits)
Experiment 36: Modeling the Dirac Equation (127-Qubits)
Experiment 35: Modeling Abstract Quantum Gravity Using Twistor Theory (127-Qubits)
Experiment 34: Conformal Invariance in Quantum Field Theory (127-Qubits)
Experiment 33: Quantum Exploration of Twistor Space (127-Qubits)
Experiment 32: Quantum Computation of Scattering Amplitudes Using Twistor Theory (127-Qubits)
Experiment 31: A Quantum-Based Secure Code Authentication App (127-Qubits)
Experiment 30: Quantum Timekeeping Using a Bloch Clock (127-Qubits)
Experiment 29: A Quantum Clock on a Bloch Sphere (127-Qubits)
Experiment 28: Investigating the Riemann Hypothesis via Quantum Path Integrals (127-Qubits)
Experiment 27: Investigating the Riemann Hypothesis via Quantum Path Integrals (50-Qubits)
Experiment 26: Quantum Simulation of Abstract Gravitational Instantons
Experiment 25: Quark-Antiquark Interaction Simulation
Experiment 24: Quantum Q-Learning
Experiment 23: Optimizing a Quantum Neuron Using Gradient Descent
Experiment 22: Exploring Quantum Chaos and Information Scrambling on an Abstract Black Hole's Event Horizon
Experiment 21: Testing Entropy, Variance, and Standard Deviation between 10 and 100 Qubits
Experiment 20: Creating a Quantum Bitcoin Seed Phrase
Experiment 19: A Quantum Neural Network
Experiment 18: Exploring Abstract Electron-Positron Annihilation
Experiment 17: A Quantum Walk
Experiment 16: Quantum Cats: Encoding a Cat in 100 Quantum States
Experiment 15: Using Quantum Cryptography to Create a Secure Bitcoin Key
Experiment 14: Reducing Entropy Through Quantum Teleportation
Experiment 13: 10-Cluster Entanglement Network
Experiment 12: 100-Qubit Quantum Entanglement
Experiment 11: Exploring Quantum Teleportation
Experiment 10: Exploring Quantum Gate-Induced Qubit Transitions
Experiment 9: Exploring Abstract Black Hole Physics
Experiment 8: Tracing Time-Dependent Quantum State Changes with the Objective Collapse Model
Experiment 7: Testing Quantum Speed Limits
Experiment 6: Visualizing Two-Qubit Superposition
Experiment 5: Quantum Superposition in Musical Representation: Beethoven's Sonata on a Quantum Keyboard
Experiment 4: Single Qubit Collapse
Experiment 3: Recreating The 2022 Nobel Prize-Winning Entanglement Experiment
Experiment 2: Thank you
Experiment 1: GitHub Download For Backend Results
Experiment 0: Public GitHub Repo
