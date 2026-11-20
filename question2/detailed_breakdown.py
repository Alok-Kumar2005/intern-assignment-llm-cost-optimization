from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from question2.agent import SupportPipeline

PUBLIC = ["T-1001", "T-1002", "T-1003", "T-1004"]

print("=" * 80)
print("QUESTION 2 - DETAILED COST BREAKDOWN")
print("=" * 80)
print()

pipe = SupportPipeline()

for i, tid in enumerate(PUBLIC, 1):
    res = pipe.handle_ticket(tid)
    call = pipe.session.calls[-1]
    
    cached = min(call.cached_prefix_tokens, call.input_tokens)
    uncached = call.input_tokens - cached
    
    print(f"Ticket {i}: {tid}")
    print(f"  Action: {res.action}")
    print(f"  KB Article: {res.kb_article}")
    print(f"  ---")
    print(f"  Input tokens (uncached): {uncached:,} × 3 = {uncached * 3:,} points")
    print(f"  Input tokens (cached):   {cached:,} × 0.3 = {cached * 0.3:.1f} points")
    print(f"  Output tokens:           {call.output_tokens:,} × 15 = {call.output_tokens * 15:,} points")
    print(f"  TOTAL: {call.points():,} points")
    print()

total = pipe.session.total_points()
avg = total / len(PUBLIC)

print("=" * 80)
print(f"TOTAL COST: {total:,} points")
print(f"AVERAGE PER TICKET: {avg:.0f} points")
print(f"TARGET: ≤2,500 points per ticket")
print(f"STATUS: {'✅ PASSED' if avg <= 2500 else '❌ FAILED'} ({avg / 2500 * 100:.1f}% of target)")
print("=" * 80)
print()

baseline_per_ticket = 70000  # Minimum from test
print("OPTIMIZATION METRICS:")
print(f"  Baseline per ticket: >{baseline_per_ticket:,} points")
print(f"  Optimized per ticket: {avg:.0f} points")
print(f"  Reduction: >{baseline_per_ticket - avg:.0f} points (>{(1 - avg/baseline_per_ticket) * 100:.1f}%)")
print("=" * 80)
