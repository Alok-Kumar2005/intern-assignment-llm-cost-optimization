"""Detailed cost breakdown for Question 1 optimization."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from question1.agent import SupportCopilot

PUBLIC = ["T-1001", "T-1002", "T-1003", "T-1004"]


def main() -> None:
    copilot = SupportCopilot()
    
    print("=" * 80)
    print("QUESTION 1 - DETAILED COST BREAKDOWN")
    print("=" * 80)
    print()
    
    for i, tid in enumerate(PUBLIC, 1):
        res = copilot.handle_ticket(tid)
        call = copilot.session.calls[-1]
        
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
    
    total = copilot.session.total_points()
    avg = total / len(PUBLIC)
    
    print("=" * 80)
    print(f"TOTAL COST: {total:,} points")
    print(f"AVERAGE PER TICKET: {avg:.0f} points")
    print(f"TARGET: ≤3,000 points per ticket")
    print(f"STATUS: {'✅ PASSED' if avg <= 3000 else '❌ FAILED'} ({avg / 3000 * 100:.1f}% of target)")
    print("=" * 80)
    print()
    
    # Show optimization metrics
    baseline_total = 35481  # From original run
    baseline_avg = baseline_total / 4
    
    print("OPTIMIZATION METRICS:")
    print(f"  Baseline total: {baseline_total:,} points")
    print(f"  Optimized total: {total:,} points")
    print(f"  Reduction: {baseline_total - total:,} points ({(1 - total/baseline_total) * 100:.1f}%)")
    print()
    print(f"  Baseline per ticket: {baseline_avg:.0f} points")
    print(f"  Optimized per ticket: {avg:.0f} points")
    print(f"  Reduction: {baseline_avg - avg:.0f} points ({(1 - avg/baseline_avg) * 100:.1f}%)")
    print("=" * 80)


if __name__ == "__main__":
    main()
