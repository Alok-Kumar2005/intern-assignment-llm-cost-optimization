# ShopAssist — support copilot cost lab

ShopAssist is a Tier-1 support agent for an e-commerce company. For each ticket it:

1. Reads the customer thread from data/tickets/
2. Loads order facts from data/orders/
3. Picks an action (REFUND, REPLACE, SEND_ARTICLE, ESCALATE_TIER2)
4. Cites the help-center article that backs the decision from data/kb/

| Track | Code | Spec |
|-------|------|------|
| Q1 - single call | [question1/agent.py](question1/agent.py) | [questions/question-1.md](questions/question-1.md) |
| Q2 - pipeline | [question2/agent.py](question2/agent.py) | [questions/question-2.md](questions/question-2.md) |

---

## How to Run and Verify

### Setup

Install the required dependencies first:

```bash
pip install -r requirements.txt
```

### Question 1 - Single Call Optimization

To run the optimized Question 1 agent:

```bash
cd question1
python run.py
```

Expected output shows 4 tickets resolved with a total cost of 6,828 points (1,707 points per ticket on average).

To verify correctness with tests:

```bash
cd ..
pytest tests/test_question1.py::test_baseline_resolves_public_tickets -v
pytest tests/test_question1.py::test_holdout_subscription -v
```

Both tests should pass, confirming all tickets return correct action and kb_article values.

To see detailed cost breakdown for each ticket:

```bash
cd question1
python detailed_breakdown.py
```

This shows input tokens, output tokens, and point costs for each individual ticket.

### Question 2 - Pipeline Optimization

To run the optimized Question 2 agent:

```bash
cd question2
python run.py
```

Expected output shows 4 tickets resolved with a total cost of 5,448 points (1,362 points per ticket on average).

To verify correctness with tests:

```bash
cd ..
pytest tests/test_question2.py::test_pipeline_resolves_public_tickets -v
```

This test should pass, confirming all tickets return correct action and kb_article values.

To see detailed cost breakdown:

```bash
cd question2
python detailed_breakdown.py
```

### Run All Tests Together

To run all correctness tests at once:

```bash
pytest tests/test_question1.py::test_baseline_resolves_public_tickets tests/test_question1.py::test_holdout_subscription tests/test_question2.py::test_pipeline_resolves_public_tickets -v
```

All three tests should pass.

---

## Expected Results

Question 1 Results:
- Total cost: 6,828 points across 4 tickets
- Per ticket average: 1,707 points (target was 3,000)
- Cost reduction: 80.8% compared to baseline
- Status: Passes target with 43% margin

Question 2 Results:
- Total cost: 5,448 points across 4 tickets
- Per ticket average: 1,362 points (target was 2,500)
- Cost reduction: Over 98% compared to baseline
- Status: Passes target with 46% margin

Correctness:
- All tickets resolve with correct action field
- All tickets cite correct kb_article
- Includes holdout test case T-1091

---

## Billing Structure

The project uses the following cost model:

- Input tokens: 3 points each
- Cached input tokens: 0.3 points each (90% discount when prefix matches)
- Output tokens: 15 points each

Formula: points = uncached_input * 3 + cached_input * 0.3 + output * 15

The shared/llm.py module provides a local simulator that calculates costs according to this formula. No real API calls are made.

---

## Solution Summary

### Question 1 Optimization

The baseline cost was 8,870 points per ticket. Main improvements:

1. Removed verbose output triggers ("think step by step") that generated 480 tokens of unnecessary reasoning. Replaced with JSON-only output of 50 tokens. Saved 6,450 points.

2. Compressed knowledge base from 600 tokens of full articles to 200 tokens of essential facts. Saved 1,200 points.

3. Removed UUID from system prompt to enable caching. Knowledge base can now be reused at 10x discount. Saved 810 points per cached call.

4. Trimmed wordy instructions and examples. Saved 750 points.

Result: 1,707 points per ticket (43% under target).

### Question 2 Optimization

The baseline cost was over 70,000 points per ticket. Main improvements:

1. Collapsed 4-node pipeline (triage, retrieve, compose, audit) into single optimized call. Eliminated three expensive round trips.

2. Removed 210,000+ token expanded help center blob. Reused compact knowledge base from Question 1.

3. Removed verbose node instructions that triggered long intermediate outputs.

4. Removed UUID traces to enable caching.

Result: 1,362 points per ticket (46% under target).

---

## Architecture Notes

The shared/llm.py module simulates an LLM with cost accounting that matches real API pricing. It does not make actual API calls. Order snapshot logic in eval/reference.py determines model responses based on order facts.

No external API key or service is required. All evaluation happens locally in Python.
