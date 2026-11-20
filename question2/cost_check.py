from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from question2.agent import SupportPipeline

PUBLIC = ["T-1001", "T-1002", "T-1003", "T-1004"]

pipe = SupportPipeline()
for tid in PUBLIC:
    pipe.handle_ticket(tid)

total = pipe.session.total_points()
avg = total / len(PUBLIC)

print(f"Total: {total:,} points")
print(f"Average per ticket: {avg:.0f} points")
print(f"Target: ≤2,500 points per ticket")
print(f"Status: {'✅ PASSED' if avg <= 2500 else '❌ FAILED'} ({avg/2500*100:.1f}% of target)")
