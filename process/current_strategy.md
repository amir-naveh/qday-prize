# Solution Strategy

## Objective
Break the largest possible ECC key (curve `y² = x³ + 7 mod p`) by running Shor's algorithm for ECDLP on real quantum hardware.

---

## Approach: Shor's Algorithm for ECDLP

The problem reduces to finding `d` such that `Q = d·G`, which is an instance of the **discrete logarithm problem on an elliptic curve group**. Shor's algorithm solves this in polynomial time on a quantum computer via quantum phase estimation.

At a high level, the quantum subroutine computes a two-register interference over the group operation, extracts a period via the **Quantum Fourier Transform (QFT)**, and classically recovers `d` from the measured output.

---

## Phases

### Phase 1 — Classical Baseline
- Implement ECC arithmetic (point addition, scalar multiplication) classically in Python
- Verify all test vectors from `contest_information/successful_curves.json`
- Solve small keys (≤10 bit) classically as ground truth for later comparison

### Phase 2 — Quantum Circuit Design (Simulator)
Build bottom-up in Classiq (Qmod), targeting the 4-bit test vector (`p=13`, `d=6`) first:
1. Quantum modular addition over `F_p`
2. Quantum modular multiplication
3. Quantum modular inverse (for ECC slope computation)
4. Quantum ECC point addition (`y² = x³ + 7 mod p`)
5. Full two-register Shor's ECDLP circuit (QPE + point addition unitary)
6. Simulate and verify output recovers correct `d`

### Phase 3 — Circuit Optimization
- Minimize qubit count and circuit depth — the primary bottleneck on real hardware
- Apply techniques: gate cancellation, qubit reuse, approximate arithmetic
- Profile T-gate count and two-qubit gate depth (the main fidelity limiters)
- Target: fit within the qubit/depth budget of accessible hardware (IBM, AWS)

### Phase 4 — Hardware Execution
- Run on real quantum hardware starting with the 4-bit key
- Use IBM Quantum or AWS Braket
- Collect shots, apply classical post-processing to extract `d` from QFT output
- Verify result against known private key from test vectors

### Phase 5 — Scale Up
- Incrementally increase key size (4 → 6 → 8 → ... bits)
- Each step: re-optimize circuit for the larger instance
- Push as high as hardware fidelity and qubit count allow before the deadline

---

## Key Technical Challenges
- **Circuit depth vs. fidelity:** deeper circuits accumulate more noise; point addition circuits are expensive
- **Qubit count:** full Shor's for ECDLP requires O(n) logical qubits; must fit within physical hardware limits
- **QFT resolution:** needs sufficient precision to recover `d` reliably

## Reference Implementations to Study
- Other public repos listed in `competition.md`

## Status
- ✅ Phase 1 — Classical baseline complete (`solution/ecc_classical.py`), all 17 test vectors verified
- ✅ Phase 2 research — Classiq capabilities documented (`solution/classiq_research.md`)
- ✅ Phase 2 implementation — `solution/shor_ecdlp_classiq.py` uses group-index encoding (Z_n), verified on simulator
- ✅ Phase 2 complete — circuit redesigned using `modular_add_constant_inplace`; both 4-bit and 6-bit verified on simulator
  - 4-bit: 11 qubits, 716 CX, d=6 ✅
  - 6-bit: 17 qubits, 2910 CX, d=18 ✅
- ✅ 7-bit simulator: 23 qubits, 7040 CX — **too deep for hardware** (exceeds ~5000 CX)
- ✅ Phase 3 — 4-bit executed on **Rigetti Ankaa-3** (AWS Braket via Classiq), d=6 recovered ✅
  - Hardware: 11 qubits, 716 CX, 4096 shots, Job `b9c03bef`
  - IBM/IonQ: fail with "insufficient budget" — AWS Braket is the active hardware path
- ⚠️  Phase 3b — 6-bit hardware: **blocked** (all hardware paths exhausted or insufficient)
  - IonQ direct: budget exhausted ($1191 spent on 4-bit alone)
  - IonQ via Braket (Forte 1): gate×shots limit allows max ~127 shots — too noisy
  - Ankaa-3: 2910 CX → ~10⁻¹² fidelity, zero signal even with 4096 shots
  - IonQ via Azure: "insufficient budget" despite $1000 allocation
  - QFT-space adder (1252 CX, 16q) verified on simulator ✅ but Forte 1 still too noisy at 127 shots
- ✅ Phase 3b fallback — 6-bit confirmed on **simulator** (ripple-carry: 17q/2910CX ✅, QFT-space: 16q/1252CX ✅)
- ❌ Phase 3c — Final 6-bit hardware attempt on IonQ Forte-1 (Job 589b1f34, 1024 shots): noise-dominated, d wrong. Post-mortem: ~31,527 shots needed for reliable signal (~$64K), far exceeding budget. **Hardware is complete.**
- 🔲 Phase 4 — Prepare competition submission: 4-bit hardware (2 devices) + 6-bit simulator
