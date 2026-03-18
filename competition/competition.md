# QDay Prize — Competitor Analysis

*Last updated: 2026-03-19*

---

## Known Public Submissions / Related Work

| Repository | Author | Approach | Hardware | Key Size | Notes |
|------------|--------|----------|----------|----------|-------|
| [adityayadav76/qday_prize_submission](https://github.com/adityayadav76/qday_prize_submission) | Aditya Yadav (CEO, Automatski) | Shor ECDLP via Qiskit on proprietary quantum computer | Automatski QC (70q, claimed 99.999% fidelity) | 7-bit, 8-bit | Reproducibility concern: requires contacting author for machine IP/port |
| [SteveTipp/Qwork.github.io](https://github.com/SteveTipp/Qwork.github.io) | Steve Tippeconnic | Shor-style ECDLP, 15-qubit circuit + classical post-processing | IBM ibm_torino (133q) | 3–6 bit | Published on arXiv (arXiv:2507.10592). Project Eleven called it "first-ever quantum attack on an ECC key." Not explicitly labeled a QDay submission. |
| [diehoq/quantum-elliptic-curve-logarithm](https://github.com/diehoq/quantum-elliptic-curve-logarithm) | diehoq | Shor's for ECDLP (Jupyter notebooks) | Not specified | Unknown | Appeared in QDay-adjacent searches; no explicit prize submission claim |

---

## Leaderboard

Official leaderboard at [qdayprize.org/leaderboard](https://www.qdayprize.org/leaderboard) shows "coming soon" — no live entries as of 2026-03-19.

---

## Key Observations

- **SteveTipp is the strongest public competitor**: 6-bit ECC broken on IBM hardware (ibm_torino), arXiv-published. Project Eleven highlighted this work. Our 4-bit result on 3 devices + 6-bit simulator is the closest comparable submission currently known.
- **Automatski submission is unverifiable**: Claims 8-bit on proprietary hardware, but no independent access to their machine. Reproducibility will be a judge concern.
- **No publicly declared winner yet**: Competition deadline is April 5, 2026.
