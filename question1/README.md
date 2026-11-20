# Question 1 — SupportCopilot

Entry point: `SupportCopilot.handle_ticket(ticket_id)`.

```bash
python run.py
pytest -q ../tests/test_question1.py
```

Use `get_ticket` / `get_order` for ticket data. Spec: [questions/question-1.md](../questions/question-1.md).

---

## Optimization Summary

The baseline implementation was expensive at 8,870 points per ticket, nearly 3x over the target of 3,000 points. I reduced this to 1,707 points per ticket, achieving an 80.8% cost reduction while maintaining 100% correctness on all test cases.

### Key Changes Made

**1. Removed Verbose Output Triggers**
The original prompt included phrases like "Think step by step" and "Write full reasoning" which triggered the simulator to generate approximately 480 tokens of unnecessary explanation text. I replaced this with a direct instruction to output only the required JSON, reducing output to around 50 tokens. This single change saved roughly 6,450 points per ticket.

**2. Compressed Knowledge Base**
The baseline loaded full markdown-formatted articles totaling about 600 tokens. I created a compressed version that presents each policy as a single line of essential facts, reducing this to approximately 200 tokens. This saved around 1,200 points per ticket.

**3. Enabled Prompt Caching**
The original system prompt included a unique UUID on every call, preventing any caching benefits. I removed this and made the system prompt static, then passed it as the `cached_prefix` parameter to the LLM client. This allows the knowledge base content to be cached at a 10x discount on subsequent calls, saving about 810 points per cached call.

**4. Streamlined Instructions and Examples**
I condensed the few-shot examples and system instructions to remove unnecessary verbosity, saving an additional 750 points per ticket through reduced input tokens.

### Results

- Total cost reduced from 35,481 to 6,828 points across 4 test tickets
- Average per ticket: 1,707 points (43% under target)
- All correctness tests pass (action and kb_article fields match expected values)
- No changes to graded output fields or parsing logic

The optimization demonstrates that significant cost savings can be achieved through careful prompt engineering without sacrificing accuracy or requiring changes to the underlying system architecture.
