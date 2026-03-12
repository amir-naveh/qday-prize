# Next Steps

Numbered list of planned and executed steps. Append new steps at the bottom.

---

1. Create initial strategy (`current_strategy.md`) — ✅ done
2. Create `solution/ecc_classical.py` — classical Python implementation of ECC arithmetic for the competition curve (`y² = x³ + 7 mod p`): point addition, scalar multiplication, and verification of all test vectors from `contest_information/successful_curves.json` — ✅ done
3. Research Classiq platform capabilities relevant to ECDLP/Shor's algorithm (quantum arithmetic, modular operations, QFT) and document findings in `solution/classiq_research.md` — ✅ done
4. Create `solution/shor_ecdlp_classiq.py` — adapt the Classiq ECDLP notebook to our competition curve (`y² = x³ + 7`, a=0, b=7), targeting the 4-bit test vector (`p=13, n=7, G=[11,5], Q=[11,8], d=6`). Include both mock (lookup-table) and full (quantum inverse) variants, with classical verification and post-processing. — ✅ done
5. Create `solution/test_postprocessing.py` — classically simulate the expected quantum measurement distribution for all 4-bit (x1, x2) pairs and verify the post-processing in `shor_ecdlp_classiq.py` correctly recovers `d=6`. Runs without a Classiq API key. — ✅ done
