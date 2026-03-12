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
- Implement the quantum circuit for Shor's ECDLP:
  - Quantum registers for the two exponents
  - Quantum elliptic curve point addition as a reversible circuit
  - QFT and measurement
- Run and validate on a quantum simulator (e.g. Qiskit's `AerSimulator`)
- Start with the smallest available key (4-bit) and verify correctness

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
- See `joes_solution/q_day_work/` — existing public attempt (Apache 2.0)
- Other public repos listed in `competition.md`
