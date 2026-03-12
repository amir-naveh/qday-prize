# Classiq Platform Research

Research into Classiq's capabilities relevant to implementing Shor's algorithm for ECDLP.

---

## Classiq Overview

Classiq is a high-level quantum programming framework with:
- **Qmod language** — high-level quantum function definitions
- **Synthesis engine** — compiles Qmod to optimized gate-level circuits
- **Cloud execution** — supports IBM, AWS Braket, IonQ, Google, Azure backends
- **Open library** — pre-built quantum functions (QFT, QPE, arithmetic, etc.)

**Workflow:** Model (Qmod) → Synthesize → Execute → Analyze

---

## Relevant Built-in Functions

### Quantum Phase Estimation
- `qpe_flexible(unitary_func, phase_register)` — applies QPE given any unitary as a lambda
- Used in Shor's factoring implementation as the core quantum subroutine

### Modular Arithmetic
- `modular_multiply_constant_inplace(n, a, x)` — computes `x = a*x mod n` in-place
- Used in Shor's factoring for modular exponentiation `a^p mod N`

### Other Primitives
- QFT, amplitude estimation, Grover operators, QSVT — all available in open library

---

## Classiq's Shor Factoring Implementation (Reference)

Located at: `algorithms/number_theory_and_cryptography/shor/shor.ipynb`

The factoring implementation uses this pattern:

```python
@qfunc
def period_finding(n: CInt, a: CInt, x: QNum, phase_var: QNum):
    x ^= 1
    qpe_flexible(
        lambda p: modular_multiply_constant_inplace(n, a**p, x),
        phase_var
    )
```

Post-processing uses classical continued fractions to extract the period `r` from the measured phase.

---

## ECDLP vs Factoring: Key Differences

Shor's for **factoring** (order-finding):
- One QPE register
- Unitary: `U_a |x⟩ = |ax mod N⟩` (modular multiplication)
- 1D phase extraction → period r → factors

Shor's for **ECDLP** (elliptic curve discrete log):
- **Two QPE registers** (s, t)
- Unitary: computes `s·G + t·Q` on the elliptic curve group
- 2D phase extraction → ratio gives `d` where `Q = d·G`
- Much more expensive: requires **quantum ECC point addition** as the core unitary

---

## What We Need to Build

Classiq does **not** have a native quantum ECC point addition function. We must implement:

1. **Quantum modular arithmetic** — modular addition, subtraction, multiplication, inverse over `F_p`
   - Can leverage Classiq's `QNum` type and arithmetic synthesis
2. **Quantum ECC point addition** — reversible quantum circuit for `(x1,y1) + (x2,y2)` on `y² = x³ + 7 mod p`
   - Built from modular arithmetic primitives
3. **Shor's ECDLP circuit** — two-register QPE using quantum point addition as the unitary
4. **Classical post-processing** — 2D continued fractions / lattice reduction to extract `d` from measured phases

---

## Implementation Plan for Phase 2

Given the complexity, implement bottom-up:

1. **Quantum modular addition** (Classiq Qmod) — simplest building block
2. **Quantum modular multiplication** — composed from additions
3. **Quantum modular inverse** — needed for point addition slope `s`
4. **Quantum ECC point addition** — combines all above
5. **Full Shor's ECDLP circuit** — two-register QPE with point addition unitary

Start with the **4-bit test vector** (`p=13`, `n=7`, `G=(11,5)`, `Q=(11,8)`, `d=6`) as the target — small enough to simulate and validate on Classiq's simulator before hardware.

---

## Resources

- Classiq docs: https://docs.classiq.io/latest/
- Classiq library (Shor's factoring): https://github.com/Classiq/classiq-library/tree/main/algorithms/number_theory_and_cryptography/shor
- QPE reference: https://github.com/Classiq/classiq-library/tree/main/algorithms/quantum_phase_estimation
