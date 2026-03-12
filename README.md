# QDay Prize — Amir Naveh (Team Classiq)

Submission repository for the [QDay Prize](https://www.qdayprize.org/) — an open competition to break the largest ECC key possible using Shor's algorithm on real quantum hardware.

**Prize:** 1 Bitcoin | **Deadline:** April 5, 2026 | **Organizer:** Project Eleven (P11)

---

## Repository Structure

```
├── goal.md                        # Master goal, strategy index, and quick reference
├── contest_information/           # Full contest details (organized for AI agent use)
│   ├── overview.md                # Prize summary, organizer, background
│   ├── technical_requirements.md  # What to build — Shor's for ECDLP, constraints, scoring
│   ├── submission_guide.md        # Submission format, required files, deadline
│   ├── curves_and_keys.md         # Test curve format and key sizes (4–21 bits)
│   ├── curves.py                  # Official curve generation script
│   ├── successful_curves.json     # Pre-generated test key vectors (4–21 bit)
│   ├── successful_curves.txt      # Same data in plaintext
│   └── faq.md                     # FAQs from qdayprize.org
├── competition.md                 # Reference links to other public submissions
├── joes_solution/                 # Reference: Joe's public solution (Apache 2.0)
├── hello_world.py                 # Sanity check script
└── log.md                         # Progress log
```

## Quick Start

**The challenge:** Given a public key `Q` and generator `G` on curve `y² = x³ + 7 (mod p)`, find private key `d` such that `Q = d * G` — using Shor's algorithm on real quantum hardware.

See [`goal.md`](./goal.md) for the full strategy and [`contest_information/technical_requirements.md`](./contest_information/technical_requirements.md) for exact technical specs.

## Submission
Submit via public GitHub repo → email to qdayprize@projecteleven.com
See [`contest_information/submission_guide.md`](./contest_information/submission_guide.md) for required files.
