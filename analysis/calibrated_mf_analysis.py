"""
Calibration-corrected matched filter analysis for ibm_fez 6-bit Shor run.

Signal circuit:  d=18, NEG_Q_STEP=13, 9 jobs × 8192 shots = 73,728 shots
Null circuit:    d=20, NEG_Q_STEP=11, 9 jobs × 8192 shots = 73,728 shots

Interleaved on same device (ibm_fez) for best noise cancellation.

Method: T_net(d) = Σ_x (counts_sig[x] - counts_null[x]) × P_ideal(x|d)
"""

import asyncio
import numpy as np
import math
from collections import defaultdict

import classiq
from classiq._internals.api_wrapper import ApiWrapper
from classiq.interface.jobs import JobID


# ─── Job IDs ─────────────────────────────────────────────────────────────────
SIGNAL_IDS = [
    '59ae7ba4-29fe-48f9-a19f-499b42441e8a',
    '83dd3487-6746-4ce7-926b-daa4ab9f5cf3',
    '5b3886d8-3e02-4205-bed7-e2d736524631',
    '0f12d67a-3dd9-46a8-ba3f-d06e903f4554',
    '413469d7-1841-447c-a6d8-b2f34ed5a28f',
    '6fde9e92-99a2-4bc3-97f3-c6a80c0a84d9',
    '2cd25075-5dc6-499a-869f-3c5fd16a8c87',
    '353d56b3-2a39-4f14-be5f-32723f7476cc',
    'ca5d01bd-ffeb-4f9b-88d6-2ff2d8af9386',
]
NULL_IDS = [
    '2d98f150-7840-4b69-a0ba-e244ce9029ac',
    '83d9a6fd-8447-4ace-aa72-48121ac221e9',
    '791cc38e-d864-4297-916a-18fe1b0b8c41',
    '2dc0a02f-989d-4095-bcb0-1097296fabee',
    'c08eae57-4ea5-4c7e-8828-394d56736899',
    'f73587c5-94a9-4895-b205-3e75e74f290d',
    '53851009-fb09-426c-9bac-1de8b417d2d9',
    '8d467ba2-b274-43df-8fdf-8c61a550b4d6',
    'c4648c55-1c8e-4cb5-8e3a-bd242469e440',
]

# ─── Circuit parameters ───────────────────────────────────────────────────────
n           = 31          # group order
N           = 32          # QPE register size (2^VAR_LEN)
IDX_BITS    = 5
INITIAL_IDX = 2
P_MOD       = 43
G_point     = (34, 3)
Q_point     = (21, 25)
KNOWN_D     = 18


# ─── Classical ECC ────────────────────────────────────────────────────────────

def point_add(P, Pt, p):
    if P is None:  return Pt
    if Pt is None: return P
    if P[0] == Pt[0]:
        if (P[1] + Pt[1]) % p == 0: return None
        s = (3 * P[0]**2) * pow(2 * P[1], -1, p) % p
    else:
        s = (Pt[1] - P[1]) * pow(Pt[0] - P[0], -1, p) % p
    xr = (s*s - P[0] - Pt[0]) % p
    yr = (s*(P[0] - xr) - P[1]) % p
    return (xr, yr)

def scalar_mult(k, P, p):
    R, Pt = None, P
    while k > 0:
        if k & 1: R = point_add(R, Pt, p)
        Pt = point_add(Pt, Pt, p)
        k >>= 1
    return R

def verify_d(d_cand):
    """Check d_cand * G == Q on the competition curve."""
    result = scalar_mult(d_cand, G_point, P_MOD)
    return result == Q_point


# ─── Build ideal probability distribution ────────────────────────────────────

def build_prob(neg_q_step):
    """
    Build prob[m1, m2, ev] = |amplitude|² for Shor ECDLP circuit
    with given neg_q_step (= (n - d_cand) % n).
    """
    omega = np.exp(2j * np.pi / N)
    amp = np.zeros((N, N, 1 << IDX_BITS), dtype=complex)
    m1_range = np.arange(N)
    m2_range = np.arange(N)
    for a in range(N):
        for b in range(N):
            ev = (INITIAL_IDX + a % n + (b * neg_q_step) % n) % n
            # amp[m1, m2, ev] += omega^(-a*m1) * omega^(-b*m2)
            col = omega**(-a * m1_range) * omega**(-b * m2_range[:, None])
            # col shape: (N, N) where col[m2, m1]
            amp[:, :, ev] += col.T   # amp[m1, m2, ev]
    amp /= N**2
    return np.abs(amp)**2   # prob[m1, m2, ev]


# ─── Parse bitstring to register values ──────────────────────────────────────

def bits_to_int(bits):
    return sum(int(b) * (1 << i) for i, b in enumerate(bits))

def parse_outcome(parsed_state):
    """Extract (m1, m2, ev) from a parsed_state dict."""
    x1b   = parsed_state.get('x1', [])
    x2b   = parsed_state.get('x2', [])
    ecpb  = parsed_state.get('ecp_phi', [])
    if len(x1b) != IDX_BITS or len(x2b) != IDX_BITS or len(ecpb) != IDX_BITS:
        return None
    m1 = bits_to_int(x1b)
    m2 = bits_to_int(x2b)
    ev = bits_to_int(ecpb)
    return m1, m2, ev


# ─── Fetch job results ───────────────────────────────────────────────────────

async def fetch_job_counts(job_id: str):
    """Fetch counts and parsed_states from a completed Classiq job."""
    result_col = await ApiWrapper.call_get_execution_job_result(
        job_id=JobID(job_id=job_id)
    )
    details = result_col.results[0].value
    counts        = dict(details.counts)          # bitstring -> int
    parsed_states = dict(details.parsed_states)   # bitstring -> dict
    return counts, parsed_states


async def merge_jobs(job_ids):
    """Fetch and merge counts/parsed_states from a list of job IDs."""
    merged_counts  = defaultdict(int)
    merged_parsed  = {}
    for jid in job_ids:
        print(f"    [{jid[:8]}] fetching...", flush=True)
        try:
            counts, parsed = await fetch_job_counts(jid)
            total = sum(counts.values())
            print(f"    [{jid[:8]}] {total} shots", flush=True)
            for bs, c in counts.items():
                merged_counts[bs] += c
            # Store parsed state for each bitstring (last one wins; they should be same)
            merged_parsed.update(parsed)
        except Exception as e:
            print(f"    [{jid[:8]}] ERROR: {e}", flush=True)
    return dict(merged_counts), merged_parsed


# ─── Matched filter ──────────────────────────────────────────────────────────

def matched_filter_score(net_counts, parsed_states, prob):
    """
    T = Σ_x net_counts[x] * prob[m1, m2, ev]
    where net_counts[x] = counts_sig[x] - counts_null[x]

    Returns (T_raw, z_score) where z_score uses null-hypothesis variance.
    Note: net_counts can be negative (null-subtracted), so z_score interpretation
    is qualitative here — we use it for ranking.
    """
    T = 0.0
    for bitstr, net_c in net_counts.items():
        ps = parsed_states.get(bitstr)
        if ps is None:
            continue
        out = parse_outcome(ps)
        if out is None:
            continue
        m1, m2, ev = out
        T += net_c * prob[m1, m2, ev]
    return T


# ─── Main analysis ───────────────────────────────────────────────────────────

async def main():
    print("Starting analysis...", flush=True)

    # Fetch all signal and null job results
    print("\nFetching signal jobs...", flush=True)
    sig_counts, sig_parsed = await merge_jobs(SIGNAL_IDS)
    sig_total = sum(sig_counts.values())
    print(f"  Total signal shots: {sig_total:,}", flush=True)

    print("\nFetching null jobs...", flush=True)
    null_counts, null_parsed = await merge_jobs(NULL_IDS)
    null_total = sum(null_counts.values())
    print(f"  Total null shots: {null_total:,}", flush=True)

    # Merge parsed_states (signal and null have same register layout)
    all_parsed = {}
    all_parsed.update(null_parsed)
    all_parsed.update(sig_parsed)

    # Build net counts: signal - null (can be negative per bitstring)
    all_bitstrings = set(sig_counts.keys()) | set(null_counts.keys())
    net_counts = {bs: sig_counts.get(bs, 0) - null_counts.get(bs, 0)
                  for bs in all_bitstrings}

    print(f"\nUnique bitstrings — signal: {len(sig_counts)}, "
          f"null: {len(null_counts)}, union: {len(all_bitstrings)}", flush=True)

    # Build ideal probability distributions and compute matched filter score
    print("\nComputing matched filter scores for all d candidates...", flush=True)
    scores = {}
    for d_cand in range(n):  # 0..30
        neg_q_step = (n - d_cand) % n
        prob = build_prob(neg_q_step)
        T = matched_filter_score(net_counts, all_parsed, prob)
        scores[d_cand] = T
        print(f"  d={d_cand:2d}  neg_q={neg_q_step:2d}  T_net={T:+.4f}", flush=True)

    # Rank by T_net score (higher = more likely)
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    print("\n" + "="*50, flush=True)
    print("Calibration-corrected matched filter rankings:", flush=True)
    print(f"{'Rank':>4}  {'d':>3}  {'T_net':>12}  {'Classical check':>16}", flush=True)
    print("-"*44, flush=True)
    for rank, (d_cand, T) in enumerate(ranked, 1):
        check = verify_d(d_cand)
        marker = " <-- CORRECT" if d_cand == KNOWN_D else ""
        check_str = "d*G==Q ✓" if check else "d*G≠Q  ✗"
        print(f"{rank:>4}  {d_cand:>3}  {T:>12.4f}  {check_str}{marker}", flush=True)
        if rank >= 10:
            print(f"  ... ({n - rank} more) ...", flush=True)
            break

    # Top-3 classical verification
    print("\n--- Top-3 Classical Verification ---", flush=True)
    for rank, (d_cand, T) in enumerate(ranked[:3], 1):
        ok = verify_d(d_cand)
        print(f"  Rank {rank}: d={d_cand}  T_net={T:+.4f}  {d_cand}*G == Q ? {'YES ✅' if ok else 'NO ❌'}", flush=True)

    # Summary
    d18_rank = next(r for r, (d, _) in enumerate(ranked, 1) if d == KNOWN_D)
    print(f"\n--- Summary ---", flush=True)
    print(f"  Signal shots: {sig_total:,}", flush=True)
    print(f"  Null shots:   {null_total:,}", flush=True)
    print(f"  d=18 rank:    {d18_rank} / {n}", flush=True)
    top1_d, top1_T = ranked[0]
    print(f"  Top-1 d={top1_d}  T_net={top1_T:+.4f}  correct={'YES ✅' if verify_d(top1_d) else 'NO ❌'}", flush=True)


if __name__ == "__main__":
    print("Authenticating with Classiq...", flush=True)
    classiq.authenticate()
    asyncio.run(main())
