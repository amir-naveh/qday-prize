# Next Steps

Numbered list of planned and executed steps. Append new steps at the bottom.

---

1. Create initial strategy (`current_strategy.md`) — ✅ done
2. Create `solution/ecc_classical.py` — classical Python implementation of ECC arithmetic for the competition curve (`y² = x³ + 7 mod p`): point addition, scalar multiplication, and verification of all test vectors from `contest_information/successful_curves.json` — ✅ done
3. Research Classiq platform capabilities relevant to ECDLP/Shor's algorithm (quantum arithmetic, modular operations, QFT) and document findings in `solution/classiq_research.md` — ✅ done
4. Create `solution/shor_ecdlp_classiq.py` — adapt the Classiq ECDLP notebook to our competition curve (`y² = x³ + 7`, a=0, b=7), targeting the 4-bit test vector (`p=13, n=7, G=[11,5], Q=[11,8], d=6`). Include both mock (lookup-table) and full (quantum inverse) variants, with classical verification and post-processing. — ✅ done
5. Create `solution/test_postprocessing.py` — classically simulate the expected quantum measurement distribution for all 4-bit (x1, x2) pairs and verify the post-processing in `shor_ecdlp_classiq.py` correctly recovers `d=6`. Runs without a Classiq API key. — ✅ done
6. Check whether Classiq 0.58.0 exposes `modular_inverse_inplace` (the full quantum version that scales to larger keys). If yes, upgrade `shor_ecdlp_classiq.py` to use it. If not, document the limitation and what version/approach is needed. — ✅ done
7. Redesign `shor_ecdlp_classiq.py` to use group-index encoding (represent ECC group as cyclic Z_n, 3 qubits instead of 8, 8-entry lookup tables instead of 256-entry). Resolve all Classiq API issues (QNum subscripting, self-referential XOR, QFT type compatibility). Synthesize and execute on Classiq simulator: **12 qubits, 1070 CX gates, depth 1424, recovered d=6 ✅** — ✅ done
8. Scale up to 6-bit test vector (p=43, n=31, d=18) — switched to `modular_add_constant_inplace` (eliminates all lookup tables and ancilla), fixed post-processing formula (d ≡ -r2·r1⁻¹ not -r1·r2⁻¹). Result: **17 qubits, 2910 CX, depth 3280, d=18 ✅** — ✅ done
9. Test 7-bit test vector (p=67, n=79, d=56) on Classiq simulator — **23 qubits, 7040 CX, depth 6452, d=56 ✅** but 7040 CX exceeds ~5000 hardware limit — ✅ done
10. Run 4-bit Shor's ECDLP circuit on real quantum hardware via Classiq. Add `run_hardware()` function using `AwsBackendPreferences(backend_name="Ankaa-3", run_via_classiq=True)`. Execute with 4096 shots and post-process to recover d=6. — ✅ done (Rigetti Ankaa-3 via AWS Braket, Job b9c03bef, d=6 ✅)
