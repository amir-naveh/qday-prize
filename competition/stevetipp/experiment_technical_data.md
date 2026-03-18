# Technical Data: ECC Key-Breaking Experiments

---

## 5-Bit ECC Key Breaking (arXiv Paper / Experiment 73)

### Circuit Parameters

From `Shors_ECC_5_Bit_Key_Run_Results_Print_0.rtf` (execution log dated 2025-06-25):

- **Script:** `Shors_ECC_5_Bit_Key.py`
- **Circuit depth:** 67,428
- **Gate counts (transpiled):**
  - `sx`: 56,613
  - `cz`: 34,319
  - `rz`: 15,355
  - `x`: 157
  - `measure`: 10
  - `barrier`: 1
- **Total transpile time:** 11,371.849 ms (~11.4 seconds)

### Backend / Hardware

- **Device:** `ibm_torino` (133-qubit IBM Heron processor)
- **Physical qubits used:** `[103, 12, 44, 94, 1, 5, 87, 64, 86, 128, 93, 125, 51, 114, 14]` (15 qubits)
- **Logical qubits:** 10 (register) + 5 ancilla = 15 total
- **Runtime:** Qiskit Runtime 2.0, version 2 options

### Run Parameters

- **Shots:** 16,384
- **Job ID:** Not stored in JSON (not present in any available file)
- **Execution date:** 2025-06-25 (from RTF log timestamp: 2025-06-25 19:41:13)
- **Submission log:** `base_primitive._run:INFO:2025-06-25 19:41:29,994: Submitting job using options {'options': {}, 'version': 2, 'support_qiskit': True}`

### JSON Result File

File: `Shors_ECC_5_Bit_Key_0.json` (also `Shors_ECC_5_Bit_Key_Break_IBM_Backend_result.json` — identical data)

```json
{
  "experiment": "ECDLP_32pts_Shors",
  "backend": "ibm_torino",
  "physical_qubits": [103, 12, 44, 94, 1, 5, 87, 64, 86, 128, 93, 125, 51, 114, 14],
  "shots": 16384,
  "counts": { ... 1015 bitstring entries, 10-bit keys ... }
}
```

- Total entries in counts: 1,015 distinct 10-bit bitstrings
- Sum of all counts: 16,384 (confirms all shots accounted for)
- Largest individual counts: `0101000000` (72), `0001000000` (64), `0100000000` (59)

### Problem Setup

- **Curve:** Order-32 elliptic curve subgroup
- **QFT outcome space:** 32 × 32
- **Target:** Extract secret scalar k from Q = kP
- **True answer:** k = 7

### Post-Processing Method (from paper + RTF log)

Classical post-processing on the 32×32 QFT outcome space:
1. Map 10-bit measurement bitstrings to (a, b) pairs using: swap halves (left = bits[:5], right = bits[5:]), then a = int(right, 2), b = int(left, 2)
2. Filter for invertible (a, b) pairs (gcd condition)
3. For each (a, b) compute candidate k = a * b^{-1} mod 32
4. Rank by shot count
5. Report top 100 results

### Claimed Results (from RTF log)

```
SUCCESS — k = 7 found in top 100 results

Top 100 invertible (a, b) pairs and recovered k:
  (a= 8, b=11)  →  k =  8   (count = 63)
  (a=12, b= 9)  →  k = 20   (count = 58)
  (a= 0, b= 3)  →  k =  0   (count = 54)
  (a= 1, b= 9)  →  k =  7   (count = 54) <<<
  (a=28, b= 1)  →  k =  4   (count = 53)
  (a= 0, b=11)  →  k =  0   (count = 53)
  (a= 8, b= 9)  →  k = 24   (count = 53)
  (a= 8, b= 3)  →  k =  8   (count = 53)
  (a= 8, b= 1)  →  k = 24   (count = 52)
  (a=16, b= 9)  →  k = 16   (count = 52)
  (a=12, b= 3)  →  k = 28   (count = 52)
  (a= 1, b=11)  →  k = 29   (count = 47)
  (a= 4, b= 3)  →  k = 20   (count = 47)
  (a=27, b= 9)  →  k = 29   (count = 47)
  (a=20, b= 9)  →  k = 12   (count = 47)
  (a=28, b= 9)  →  k =  4   (count = 46)
  (a=24, b= 3)  →  k = 24   (count = 46)
  (a= 0, b= 1)  →  k =  0   (count = 46)
  (a=24, b= 9)  →  k =  8   (count = 45)
  (a= 0, b= 9)  →  k =  0   (count = 45)
  (a= 4, b= 1)  →  k = 28   (count = 45)
  (a= 9, b= 9)  →  k = 31   (count = 44)
  (a=12, b=11)  →  k = 28   (count = 43)
  (a=16, b= 3)  →  k = 16   (count = 43)
  (a= 1, b= 1)  →  k = 31   (count = 43)
  (a=10, b= 1)  →  k = 22   (count = 42)
  (a=16, b= 1)  →  k = 16   (count = 42)
  (a= 4, b=11)  →  k = 20   (count = 42)
  (a=20, b= 1)  →  k = 12   (count = 41)
  (a=17, b= 1)  →  k = 15   (count = 41)
  (a=26, b= 1)  →  k =  6   (count = 41)
  (a=11, b= 3)  →  k =  7   (count = 41) <<<
  (a=10, b=11)  →  k =  2   (count = 41)
  (a=16, b=11)  →  k = 16   (count = 40)
  (a= 5, b= 1)  →  k = 27   (count = 40)
  (a=14, b= 9)  →  k =  2   (count = 40)
  (a=28, b= 3)  →  k = 12   (count = 40)
  (a= 4, b= 9)  →  k = 28   (count = 40)
  (a=30, b= 9)  →  k = 18   (count = 39)
  (a=24, b=11)  →  k = 24   (count = 39)
  (a= 2, b=11)  →  k = 26   (count = 39)
  (a=28, b=11)  →  k = 12   (count = 39)
  (a=17, b= 9)  →  k = 23   (count = 39)
  (a= 1, b= 3)  →  k = 21   (count = 39)
  (a= 2, b= 9)  →  k = 14   (count = 38)
  (a=27, b= 1)  →  k =  5   (count = 38)
  (a=15, b=11)  →  k = 19   (count = 38)
  (a=31, b= 1)  →  k =  1   (count = 38)
  (a=12, b= 1)  →  k = 20   (count = 37)
  (a= 9, b= 1)  →  k = 23   (count = 37)
  (a=25, b= 3)  →  k = 13   (count = 37)
  (a=17, b=11)  →  k = 13   (count = 37)
  (a=25, b=11)  →  k = 21   (count = 37)
  (a=14, b=11)  →  k = 22   (count = 36)
  (a=26, b=11)  →  k = 18   (count = 36)
  (a=24, b= 1)  →  k =  8   (count = 36)
  (a=10, b= 3)  →  k = 18   (count = 36)
  (a=13, b= 1)  →  k = 19   (count = 36)
  (a= 9, b=11)  →  k =  5   (count = 36)
  (a= 3, b= 3)  →  k = 31   (count = 36)
  (a=15, b= 9)  →  k =  9   (count = 35)
  (a=13, b= 9)  →  k = 27   (count = 35)
  (a=13, b=11)  →  k = 25   (count = 35)
  (a=26, b= 9)  →  k = 22   (count = 35)
  (a= 5, b= 3)  →  k =  9   (count = 34)
  (a= 9, b= 3)  →  k = 29   (count = 34)
  (a=29, b= 1)  →  k =  3   (count = 33)
  (a=11, b=11)  →  k = 31   (count = 33)
  (a= 2, b= 3)  →  k = 10   (count = 33)
  (a= 3, b= 1)  →  k = 29   (count = 32)
  (a=15, b= 1)  →  k = 17   (count = 32)
  (a=20, b= 3)  →  k =  4   (count = 32)
  (a=30, b=11)  →  k =  6   (count = 32)
  (a=25, b= 1)  →  k =  7   (count = 32) <<<
  (a=19, b= 9)  →  k =  5   (count = 31)
  (a=29, b= 9)  →  k = 11   (count = 31)
  (a= 3, b= 9)  →  k = 21   (count = 31)
  (a= 5, b=11)  →  k = 17   (count = 31)
  (a=17, b= 3)  →  k =  5   (count = 30)
  (a= 0, b=17)  →  k =  0   (count = 30)
  (a=30, b= 1)  →  k =  2   (count = 30)
  (a= 6, b=11)  →  k = 14   (count = 30)
  (a=11, b= 1)  →  k = 21   (count = 29)
  (a=18, b= 3)  →  k = 26   (count = 29)
  (a=21, b= 9)  →  k = 19   (count = 29)
  (a=10, b= 9)  →  k =  6   (count = 29)
  (a= 2, b= 1)  →  k = 30   (count = 29)
  (a=25, b= 9)  →  k = 15   (count = 28)
  (a= 8, b=19)  →  k =  8   (count = 28)
  (a= 5, b= 9)  →  k =  3   (count = 28)
  (a= 3, b=11)  →  k = 23   (count = 28)
  (a=10, b=17)  →  k = 22   (count = 28)
  (a=20, b=11)  →  k =  4   (count = 28)
  (a=31, b=11)  →  k =  3   (count = 28)
  (a=26, b= 3)  →  k =  2   (count = 27)
  (a=29, b=11)  →  k =  9   (count = 27)
  (a=14, b= 1)  →  k = 18   (count = 27)
  (a= 7, b= 1)  →  k = 25   (count = 27)
  (a=23, b=11)  →  k = 27   (count = 27)
  (a= 8, b=25)  →  k = 24   (count = 27)
```

Note: k=7 appears three times in top 100:
  - (a=1, b=9) → k=7, count=54 (rank ~4)
  - (a=11, b=3) → k=7, count=41 (rank ~32)
  - (a=25, b=1) → k=7, count=32 (rank ~73)

The highest-ranked result was (a=8, b=11) → k=8 (count=63). k=7 is NOT the top result; it appears in top 100.

### Independent Analysis Results (FIVE_BIT_INTERFERENCE_ANALYSIS_NOTE.md)

Best achievable with post-processing improvements:
- `best_k = 0` (NOT 7 — k=7 never reaches rank 1)
- `true_rank = 3` (k=7 reaches rank 3 at best with weighted exact-line scoring)
- `true_k_rank_1_rate = 0.0` (k=7 NEVER wins in 500 bootstrap replicates)
- `true_k_top_3_rate = 0.472`
- `true_k_top_5_rate = 0.806`
- k=0 wins all 500/500 bootstrap replicates as rank-1

---

## 6-Bit ECC Key Breaking (Experiment 76)

### Circuit Parameters

Derived from `Shors_ECC_6_Bit_Key_0.json`:

- **Circuit name/experiment:** `ECDLP_64pts_Shors`
- **Qubits:** 18 (12 logical + 6 ancilla)
- **Physical qubits:** `[1, 14, 64, 42, 103, 54, 55, 44, 94, 111, 16, 87, 98, 11, 51, 124, 18, 59]`
- (Note: circuit depth and gate counts not stored in JSON; would be in a separate RTF/log file)

### Backend / Hardware

- **Device:** `ibm_torino` (133-qubit)
- **Runtime:** Qiskit Runtime 2.0

### Run Parameters

- **Shots:** 16,384
- **QFT outcome space:** 64 × 64
- **Total count entries:** 3,883 distinct 12-bit bitstrings

### Problem Setup

- **Curve:** Order-64 elliptic curve subgroup
- **True answer:** k = 42

### JSON Result File

```json
{
  "experiment": "ECDLP_64pts_Shors",
  "backend": "ibm_torino",
  "physical_qubits": [1, 14, 64, 42, 103, 54, 55, 44, 94, 111, 16, 87, 98, 11, 51, 124, 18, 59],
  "shots": 16384,
  "counts": { ... 3883 entries, 12-bit keys ... }
}
```

### Post-Processing Method (6-bit, Method 6 — current best)

From `Shors_ECC_6_Bit_Key_0_Method6_Postprocessed.json`:
- `derived_from`: `method6_postprocessed_6bit_analysis_pipeline`
- `mapping`: `split_left_right_reverse_each_half`
  - first half → a, second half → b, reverse bits inside each half
- `order`: 64
- `register_bits`: 6
- `true_k`: 42
- `method_name`: `Method 6`
- `scoring_mode`: `parity_even_odd_then_capped_weighted_exact_line_row_centered_positive_residual`
- Preprocessing steps: `['toroidal_3x3_smoothing', 'even_odd_parity_sector', 'capped_weight_weighted_exact_line_context', 'row_centered_positive_residual']`

### Claimed Results (6-bit)

After Method 6 post-processing:
- `best_k = 40` (NOT 42)
- `true_rank = 3` (k=42 ranks 3rd)
- `true_k_rank_1_rate = 0.0` (k=42 never wins in bootstrap)
- `true_k_top_3_rate = 0.142`
- `true_k_top_5_rate = 0.246`

Rank-1 winner in bootstrap: k=40 wins 182/500, k=30 wins 118/500; k=42 wins only 21/500.

---

## Phase-Only 5-Bit Run (Experiment 81)

File: `Shor-style_5_Bit_Key_Phase_Only_0.json`

```json
{
  "experiment": "ECDLP_32pts_PhaseOnly",
  "backend": "ibm_marrakesh",
  "physical_qubits": [94, 35, 2, 5, 53, 21, 13, 55, 23, 7],
  "shots": 16384
}
```

- **Device:** `ibm_marrakesh` (156-qubit IBM Eagle processor) — different from arXiv paper
- **Qubits:** 10 physical
- Total count entries: 791

---

## Additional Run: 5-Bit SingleQFT RealOracle (Experiment from noise study)

File: `Shors_ECC_5_Bit_SingleQFT_RealOracle_0.json`

```json
{
  "experiment": "ECDLP_32pts_Shors_singleQFT",
  "backend": "ibm_fez",
  "physical_qubits": [131, 143, 125, 41, 9, 151, 45, 121, 28, 141, 105, 2, 117, 145, 106],
  "shots": 16384,
  "P_IDX": 1,
  "Q_IDX": 23,
  "ORDER": 32
}
```

- **Device:** `ibm_fez` — yet another backend used for noise study

---

## 4-Bit Reference Run (Experiment 72)

File: `Shors_ECC_4_Bit_Key_0.json`

```json
{
  "experiment": "ECDLP_16pts_Shors",
  "backend": "ibm_torino",
  "physical_qubits": [12, 5, 1, 103, 64, 124, 65, 52, 128, 99, 38, 94],
  "shots": 16384
}
```

- 12 physical qubits (8 logical + 4 ancilla)
- Total count entries: 256 (fully saturated 8-bit space — 2^8 = 256)

---

## Summary Table

| Experiment | Key bits | Backend | Qubits (phys) | Shots | Circuit depth | CZ gates | True k | k found rank-1? | k in top 100? |
|---|---|---|---|---|---|---|---|---|---|
| E73 (arXiv paper) | 5-bit | ibm_torino | 15 | 16,384 | 67,428 | 34,319 | 7 | No (rank ~4 naive, rank 3 best PP) | Yes |
| E76 | 6-bit | ibm_torino | 18 | 16,384 | unknown | unknown | 42 | No (rank 3 best PP) | unclear |
| E81 | 5-bit phase-only | ibm_marrakesh | 10 | 16,384 | unknown | unknown | 7 | unknown | unknown |
| E72 | 4-bit | ibm_torino | 12 | 16,384 | unknown | unknown | unknown | unknown | unknown |
| Noise study | 5-bit singleQFT | ibm_fez | 15 | 16,384 | unknown | unknown | 7 | unknown | unknown |

Notes on 5-bit circuit gates (transpiled to ibm_torino native gate set):
- Native gates used: sx, cz, rz, x (Heron r2 basis)
- CZ is the 2-qubit entangling gate (ibm_torino uses CZ, not CX/CNOT)
- 34,319 CZ gates total

---

## Key Files in Repo

| File | Description |
|---|---|
| `Shors_ECC_5_Bit_Key_0.json` | Main 5-bit raw backend result (arXiv paper) |
| `Shors_ECC_5_Bit_Key_Break_IBM_Backend_result.json` | Same data, alternate filename |
| `Shors_ECC_5_Bit_Key_Run_Results_Print_0.rtf` | Full execution log with circuit stats and top-100 output |
| `Shors_ECC_6_Bit_Key_0.json` | 6-bit raw backend result |
| `Shors_ECC_6_Bit_Key_0_Method6_Postprocessed.json` | 6-bit Method 6 post-processed result |
| `Shor-style_5_Bit_Key_Phase_Only_0.json` | Phase-only variant on ibm_marrakesh |
| `Shors_ECC_5_Bit_SingleQFT_RealOracle_0.json` | SingleQFT oracle variant on ibm_fez |
| `FIVE_BIT_INTERFERENCE_ANALYSIS_NOTE.md` | Statistical analysis of 5-bit result |
| `SIX_BIT_INTERFERENCE_ANALYSIS_NOTE.md` | Statistical analysis of 6-bit result |
| `P11_QDAY_README.md` | QDay Prize submission info (6-bit key) |
| `5_Bit_Shor_Style_IBM_Backend_JSON_arXiv_and_Noise.zip` | Zip of arXiv + noise run JSONs |
| `6_Bit_Shor_Style_IBM_Backend_JSON.zip` | Zip of 6-bit run JSONs |
| `qwork_codex_reanalysis_5bit_ecc_key_result.zip` | Codex re-analysis of 5-bit |
| `qwork_codex_reanalysis_6bit_ecc_key_result.zip` | Codex re-analysis of 6-bit |
| `Steve_Tippeconnic_Phase-Only Shor-Style Recovery of a 5-Bit Scalar in an Order-32 Elliptic Curve Subgroup.pdf` | Companion paper for E81 |
