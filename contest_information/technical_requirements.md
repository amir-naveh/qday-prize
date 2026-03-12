# Technical Requirements

## The Problem
Solve the **Elliptic Curve Discrete Logarithm Problem (ECDLP)**:

Given:
- An elliptic curve `E` over a finite field `F_p`
- A generator point `G` on the curve
- A public key `Q = d * G`

Find the **private key `d`** using Shor's algorithm on a quantum computer.

## The Curve
All competition keys use the curve:

```
y² = x³ + 7  (mod p)
```

This is the same form as Bitcoin's secp256k1 curve. Parameters:
- Curve parameter `a = 0`, `b = 7`
- Prime field modulus `p` (varies by bit size)
- All curves have cofactor `h = 1` (prime-order subgroups)
- Primes satisfy: `p > 3`, `p ≠ 7`, `p ≡ 1 (mod 3)` (non-supersingular)

## What Must Be Implemented
1. **Shor's algorithm for ECDLP** on actual quantum hardware
2. Must run on gate-level quantum circuits
3. Must derive the private key `d` from the public key `Q` and generator `G`

## Constraints
- Must run on **real quantum hardware** (not simulation)
- Must use **Shor's algorithm** specifically
- Solution must be **general and robust** — not a one-off hack
- Must not rely on **impractical classical pre/post-processing** that doesn't scale toward 256-bit keys
- Cannot rely on **compilation tricks** that don't generalize to larger key sizes

## Quantum Hardware Access
Quantum computers can be accessed via:
- **AWS Braket**
- **IBM Quantum**
- Any other accessible quantum hardware

## Scoring / Ranking
- **Larger key sizes = higher rank**
- Breaking a 5-bit key automatically covers all smaller sizes
- Even a **3-bit key** would be a significant and publishable result
- The goal is to maximize the bit size of the broken key

## Key Bit Sizes Available for Testing
Competition provides test keys from **3 to 21 bits** (see `curves_and_keys.md`).
