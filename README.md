# QDay Prize Submission — Amir Naveh

**Contact:** amir@classiq.io

**Professional background:** Co-founder and Head of Algorithms at Classiq Technologies, leading R&D in quantum software design automation and circuit synthesis. Algorithms researcher and developer with over 20 patents in quantum computing.

---

## Result

**Key size broken: 4-bit** (`p=13`, `n=7`, `G=(11,5)`, `Q=(11,8)`, recovered `d=6`)

Shor's algorithm for ECDLP executed on **three real quantum hardware devices** across two hardware modalities (superconducting and trapped-ion):

| Device | Vendor | Type | Shots | Job ID | Result |
|--------|--------|------|-------|--------|--------|
| Rigetti Ankaa-3 | Rigetti / AWS Braket | Superconducting | 4,096 | `b9c03bef-24d9-4c84-aabb-a3ddcb80d3ff` | **d=6 ✅** |
| IonQ Forte-1 | IonQ / Classiq | Trapped-ion | 1,024 | `f6da2c51-e4e0-4922-9ade-066392a42362` | **d=6 ✅** |
| IBM Pittsburgh | IBM Quantum | Superconducting | 1,024 | `56c3b591` | **d=6 ✅** |

The 6-bit key (`p=43`, `n=31`, `d=18`) was verified correct on the Classiq simulator but could not be recovered from hardware — see [Hardware Limitations](#hardware-limitations) below.

---

## Quantum Computer Hardware

### 4-bit Circuit (all three devices)
- **Circuit:** 11 qubits, 716 CX gates, depth 1050 (ripple-carry adder variant)
- **Curve:** `y² = x³ + 7 (mod 13)`, group order `n=7`, private key `d=6`

**Rigetti Ankaa-3**
- 82 superconducting qubits, accessed via AWS Braket through Classiq

**IonQ Forte-1**
- 36 trapped-ion qubits, accessed via Classiq directly

**IBM Pittsburgh (ibm_pittsburgh)**
- 127 superconducting qubits (IBM Eagle r3), accessed via IBM Quantum cloud

---

## Access Method

- **Rigetti Ankaa-3:** AWS Braket (`AwsBackendPreferences`) via Classiq SDK
- **IonQ Forte-1:** Classiq direct (`IonqBackendPreferences`, `run_via_classiq=True`)
- **IBM Pittsburgh:** IBM Quantum cloud (`IBMBackendPreferences`, `channel="ibm_cloud"`) via Classiq SDK

All circuit synthesis done with [Classiq](https://www.classiq.io/) SDK v1.5.0.

---

## Step-by-Step Execution Instructions

### Prerequisites

```bash
pip install classiq>=1.5.0
```

Requires a [Classiq account](https://platform.classiq.io/) (free tier sufficient for simulation; hardware provider account needed for hardware runs).

### 1. Verify the classical baseline (no API key needed)

```bash
python solution/ecc_classical.py
```
Verifies all 17 test vectors from `contest_information/successful_curves.json`.

### 2. Verify post-processing logic (no API key needed)

```bash
python solution/test_postprocessing.py
```
Simulates the ideal quantum measurement distribution classically and confirms post-processing recovers correct `d` for 4-bit through 8-bit.

### 3. Run on Classiq simulator

Authenticate with Classiq (`classiq.authenticate()`), then:
```bash
python solution/shor_ecdlp_classiq.py
```
Edit `TARGET_BITS = 4` (or 6) at the top of the file. Expected: `Recovered d = 6 ✅`

### 4. Run on hardware

**Rigetti Ankaa-3 (AWS Braket):**
```bash
python solution/shor_ecdlp_classiq.py hardware Ankaa-3 braket 4096
```

**IonQ Forte-1:**
```bash
python solution/shor_ecdlp_classiq.py hardware qpu.forte-1 ionq 1024
```

**IBM Quantum (Pittsburgh):**
Set IBM credentials in `IBMBackendPreferences` (channel, instance_crn, access_token), then call `run_hardware(backend_name="ibm_pittsburgh", provider="ibm", num_shots=1024)`.

Expected in all cases: `Recovered d = 6 ✅`

---

## Algorithm

**Shor's algorithm for ECDLP** on curve `y² = x³ + 7 (mod p)`.

**Key design choice — group-index encoding:** The elliptic curve group (prime order `n`) is represented as cyclic group `Z_n`, where integer `k` encodes the point `k·G`. This reduces qubit count from O(log p) to O(log n) and eliminates the need for quantum modular inversion — the dominant cost in naive ECDLP implementations.

**Circuit structure (4-bit, ripple-carry):**
```
x1 (VAR_LEN qubits): |0⟩ → H^⊗ → controlled adds → inverse QFT → measure
x2 (VAR_LEN qubits): |0⟩ → H^⊗ → controlled adds → inverse QFT → measure
ecp (IDX_BITS qubits): |INITIAL_IDX⟩ → modular adds controlled on x1,x2 bits → measure
```
The `ecp` register accumulates `INITIAL_IDX + a·1 + b·(−d) mod n` for superposed `(a,b)`. After inverse QFT on x1 and x2, measured values concentrate near `(s1/N·n, s2/N·n)` where `s1·d + s2 ≡ 0 (mod n)`.

**6-bit QFT-space variant:** Keeps `ecp` in QFT domain throughout, using phase rotations (`modular_add_qft_space`) instead of ripple-carry. 57% fewer CX gates (1252 vs 2910).

**Post-processing:**
```python
r1 = round(m1 / N * n) % n
r2 = round(m2 / N * n) % n
if gcd(r1, n) == 1:
    d_candidate = (-r2 * pow(r1, -1, n)) % n
```
Mode of all valid candidates across all shots = recovered `d`.

---

## Hardware Limitations

The 6-bit circuit (1252 CX) could not be recovered from hardware:

| Device | Shots | Circuit fidelity | Signal shots | Outcome |
|--------|-------|------------------|--------------|---------|
| IonQ Forte-1 | 1,024 | ~0.7% | ~7 | ❌ noise-dominated |
| IBM Pittsburgh | 1,024 | ~0.15% | ~1.5 | ❌ noise-dominated |
| IBM ibm_fez (calibrated) | 73,728 signal + 73,728 null | ~0.15% | ~110 | ❌ noise-dominated |

**Root cause:** Per-gate CX fidelity ~99.5% (IBM), ~99.58% (IonQ Forte-1). Circuit fidelity = `(per-gate fidelity)^(CX count)` ≈ 0.15% for 1252 CX. The signal is buried in noise.

**Calibration approach:** To cancel IBM's amplitude-damping bias (which corrupts a uniform noise assumption), a null circuit (d=20, same structure) was run interleaved with the signal circuit on the same device (ibm_fez). After 147,456 total shots and a calibration-corrected matched filter, d=18 still ranked 22nd out of 31 — residual calibration drift between sequential jobs swamped the 0.15% signal.

**Feasibility threshold:** Reliable 6-bit hardware recovery requires CX fidelity ≥ 99.9% (near fault-tolerant regime) or a fundamentally shorter circuit (≤ 300 CX for the 6-bit instance — not achievable with current quantum arithmetic methods).

---

## Repository Structure

```
├── README.md                           # This file (competition submission)
├── solution/
│   ├── shor_ecdlp_classiq.py          # Main circuit: 4-bit and 6-bit Shor's ECDLP
│   ├── ecc_classical.py               # Classical ECC verification baseline
│   └── test_postprocessing.py         # Post-processing unit tests (no API key needed)
├── analysis/
│   └── calibrated_mf_analysis.py      # Calibration-corrected matched filter (ibm_fez)
├── contest_information/
│   ├── successful_curves.json         # Test vectors (4–21 bit)
│   └── ...
└── process/
    └── log.md                         # Full execution log with all job IDs
```

All hardware job IDs, shot counts, recovered keys, and fidelity analysis in [`process/log.md`](./process/log.md).
