# Test Curves and Keys

## Summary
The competition provides pre-generated ECC test vectors for key sizes **4 to 21 bits** (bit sizes 1–3 yielded no valid candidate primes under the constraints; bit size 5 found no valid curve).

## Curve Definition
All curves use the form:
```
y² = x³ + 7  (mod p)
```
Generated with **seed = 536** for reproducibility.

## Available Downloads
- `curves.txt` — plaintext format: https://www.qdayprize.org/curves.txt
- `curves.json` — JSON format: https://www.qdayprize.org/curves.json
- `curves.py` — generation script (also saved as `curves.py` in this directory)

## Data Format (per entry)
| Field | Description |
|-------|-------------|
| `bit_length` | Key size in bits |
| `prime` | Field prime `p` |
| `curve_order` | Number of points on the curve `#E` |
| `subgroup_order` | `n` — largest prime factor of `#E` |
| `cofactor` | `h = #E / n` (always 1 in these curves) |
| `generator_point` | `[Gx, Gy]` — base point `G` |
| `private_key` | `d` — the secret to recover |
| `public_key` | `[Qx, Qy]` where `Q = d * G` |

## The Challenge
Given `p`, `G`, `n`, and `Q`, find `d` such that `Q = d * G`.

## Known Test Vectors (summary)

| Bits | Prime (p) | Private Key (d) | Public Key Q (x, y) |
|------|-----------|-----------------|----------------------|
| 4 | 13 | 6 | [11, 8] |
| ... | ... | ... | ... |
| 21 | 1,048,783 | 653,735 | [1,047,961, 428,633] |

> Full data: download `curves.json` from the URL above or run `curves.py` locally.

## Scoring
- Successfully breaking an N-bit key qualifies your submission for all key sizes ≤ N
- **Maximize N** — the team with the largest N wins
- Even a **3 or 4-bit key** is a historic and publishable result on real quantum hardware

## Curve Generation Constraints (from curves.py)
- `p > 3`
- `p ≠ 7` (avoids singular curve for y² = x³ + 7)
- `p ≡ 1 (mod 3)` (ensures curve is not supersingular)
- Cofactor `h ≤ 2` (ensures large subgroup)
- All successful curves have `h = 1`
