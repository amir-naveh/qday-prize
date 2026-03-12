# Frequently Asked Questions

## How do I compete?
Register at qdayprize.org, then implement Shor's algorithm for ECDLP on real quantum hardware. Submit via a public GitHub repo emailed to qdayprize@projecteleven.com.

## How do I prove I used a quantum computer?
Provide:
- Gate-level quantum program description
- Detailed explanation of techniques used
- Description of the quantum computer hardware
- Platform log files

An independent panel will attempt to verify results.

## Can I enter as a team or organization?
Yes. Teams, research groups, and organizations can enter. Designate one person as the official point of contact. No institutional affiliation required.

## Who funds and organizes this?
**Project Eleven (P11)** — https://projecteleven.com. Fully backed and organized by them.

## How do you ensure results are legitimate?
A judging panel of cryptographers and quantum computing experts reviews all submissions. They verify quantum computer execution and rule compliance. Falsified or unverifiable results = disqualification.

## Who owns the IP?
Competitors retain ownership of their work. However, **submissions and key findings will be made public** for transparency. Results cannot remain private.

## What key sizes should I target?
- Any key size broken is significant — even **3 or 4 bits** on real quantum hardware would be historic
- The competition provides test keys from **4 to 21 bits**
- Higher bit sizes = higher rank and more likely to win

## What quantum platforms can I use?
- **AWS Braket**
- **IBM Quantum**
- Any other accessible quantum hardware

## Do I need my own quantum computer?
No. You can use cloud-accessible quantum hardware (AWS Braket, IBM Quantum, etc.).

## Does the quantum computer need to be publicly accessible?
No. The quantum computer you use does not need to be publicly accessible.

## What algorithm must I use?
**Shor's algorithm** — specifically for the Elliptic Curve Discrete Logarithm Problem (ECDLP). Solutions must be general, not one-off tricks that don't scale.

## What curves/keys are used?
The curve `y² = x³ + 7 (mod p)` — the same form as Bitcoin's secp256k1. Test vectors from 4 to 21 bits are provided. See `curves_and_keys.md`.

## Evaluation rubric?
Full rubric: https://www.qdayprize.org/q-day-rubric.pdf
