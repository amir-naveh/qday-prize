# Project Goal

## Objective
**Win the QDay Prize** — awarded to the team that breaks the largest ECC key using Shor's algorithm on a real quantum computer.

- **Prize:** 1 Bitcoin
- **Deadline:** April 5, 2026
- **Organizer:** Project Eleven (P11) — qdayprize@projecteleven.com

## The Task
Implement Shor's algorithm for the **Elliptic Curve Discrete Logarithm Problem (ECDLP)** and run it on real quantum hardware to recover a private key `d` from a public key `Q = d * G`.

The curve is: `y² = x³ + 7 (mod p)` — same form as Bitcoin's secp256k1.

## Winning Criteria
- Break the **largest key size possible** (test keys range from 4 to 21 bits)
- Any key size broken on real quantum hardware is significant — even 4 bits
- Submit via a **public GitHub repo** emailed to qdayprize@projecteleven.com

## Every Action Must Serve This Goal
All work in this project — algorithm design, circuit implementation, hardware testing, classical pre/post-processing — must be directed toward maximizing the bit size of the ECC key broken on real quantum hardware before April 5, 2026.

---

## Contest Information Index

All detailed contest information is in the `contest_information/` directory:

| File | Contents |
|------|----------|
| `overview.md` | Prize summary, organizer, deadline, background |
| `technical_requirements.md` | Exactly what must be built — Shor's for ECDLP, constraints, scoring |
| `submission_guide.md` | How to submit, required files (code, brief.pdf, README.md), deadlines |
| `curves_and_keys.md` | Test curve format, available key sizes (4–21 bits), data fields |
| `curves.py` | Official Python script to generate/reproduce all test curves and keys |
| `faq.md` | FAQ — verification, IP, platforms, rules |

## Quick Reference

### What to build
- Gate-level quantum circuit implementing Shor's algorithm for ECDLP
- Must run on real quantum hardware (AWS Braket, IBM Quantum, or other)
- Must be general (not a one-off trick) and scalable in principle

### What to submit (GitHub repo)
1. Working code that runs on quantum hardware and recovers `d` from `Q`
2. `brief.pdf` (≤2 pages) — approach, techniques, hardware requirements
3. `README.md` — email, background, key length broken, hardware used, run instructions
4. Platform log files and supporting analysis

### Test curve (example — 4-bit)
```
Curve: y² = x³ + 7 (mod 13)
Generator G: (11, 5)
Private key d: 6       ← THIS is what the quantum algorithm must find
Public key Q: (11, 8)  ← This is given as input
```

### Full rubric
https://www.qdayprize.org/q-day-rubric.pdf
