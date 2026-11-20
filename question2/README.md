# Question 2 — SupportPipeline

Entry point: `SupportPipeline.handle_ticket(ticket_id)`.

```bash
python run.py
pytest tests/test_question2.py::test_pipeline_resolves_public_tickets -v
```

Spec: [questions/question-2.md](../questions/question-2.md).

---

## Optimization Summary

The baseline pipeline used four separate LLM calls (triage, retrieve, compose, audit) and loaded over 200,000 tokens of expanded help center content, resulting in costs well over 70,000 points per ticket. The target was 2,500 points per ticket. I reduced this to 1,362 points per ticket, a massive cost reduction while maintaining 100% correctness.

### Key Changes Made

**1. Collapsed the Four-Node Pipeline into One Call**
The baseline made four separate API calls with overlapping context passed between nodes. Each call loaded massive amounts of redundant data and generated verbose intermediate outputs. I replaced this with a single optimized decision call that gets the answer directly, eliminating three expensive round trips and all the intermediate token overhead.

**2. Removed the Massive Help Center Blob**
The original loaded 210,000+ tokens of expanded help center content (including filler text) into multiple calls. I replaced this with the same compact 200-token knowledge base from Question 1, containing only the essential policy facts needed to make correct decisions.

**3. Eliminated Verbose Instructions**
Each pipeline node had instructions like "restate the ticket step by step", "print full text of eight articles", "full reasoning", and "double-check and restate". These triggered massive verbose outputs at every stage. I replaced all of this with a single concise instruction to output JSON only.

**4. Enabled Caching**
The baseline included UUID traces that prevented caching. I removed these and passed the system prompt as cached_prefix, allowing the knowledge base to be reused at 10x discount across calls.

### Results

- Total cost reduced from 70,000+ to 5,448 points across 4 test tickets
- Average per ticket: 1,362 points (46% under target)
- All correctness tests pass (action and kb_article fields match expected values)
- Massive reduction in both API calls (4 to 1) and tokens per call

The key insight was recognizing that the multi-stage pipeline was solving the same problem as Question 1 but with unnecessary complexity. By applying the same optimization principles and collapsing the pipeline, I achieved even better cost efficiency than the target required.
