from __future__ import annotations

import json
from dataclasses import dataclass

from shared.billing import CostSession
from shared.kb import article_ids, load_article
from shared.llm import ChatMessage, LlmClient
from shared.tools import format_thread, get_order, get_ticket

from question1.agent import parse_resolution


@dataclass
class TicketResolution:
    action: str
    kb_article: str


# Compact KB for Question 2
_COMPACT_KB = """returns-within-30-days: Physical items, resalable condition, refund ≤30 days
digital-license-no-refund: Digital products not refundable after license revealed
custom-items-no-replace: Custom items not eligible for auto replacement, escalate Tier 2
damage-replacement-7-days: Catalog items damaged ≤7 days get free replacement
subscription-cooling-off: Annual subscriptions prorated refund if cancelled ≤30 days"""


class SupportPipeline:
    """Same product as Question 1 — triage, retrieve, compose, audit."""

    def __init__(self, session: CostSession | None = None):
        self.session = session or CostSession()
        self.llm = LlmClient(self.session)

    def handle_ticket(self, ticket_id: str) -> TicketResolution:
        ticket = get_ticket(ticket_id)
        order = get_order(ticket["order_id"])
        thread = format_thread(ticket)
        snapshot = json.dumps(order, indent=2)

        # Simplified pipeline - skip verbose intermediate steps
        final = self._decide(ticket_id, thread, snapshot)
        parsed = parse_resolution(final)
        return TicketResolution(parsed.action, parsed.kb_article)

    def _decide(self, ticket_id: str, thread: str, snapshot: str) -> str:
        """Single optimized decision step with caching."""
        system_content = "\n".join([
            "ShopAssist support pipeline.",
            f"KB:\n{_COMPACT_KB}",
            'Output JSON: {"action":"<ACTION>","kb_article":"<article-id>","customer_reply":"<reply>"}',
        ])
        
        messages = [
            ChatMessage("system", system_content),
            ChatMessage(
                "user",
                f"TICKET {ticket_id}\nTHREAD:\n{thread}\nORDER_SNAPSHOT:\n{snapshot}\nEND_SNAPSHOT"
            ),
        ]
        
        return self.llm.chat("decide", messages, cached_prefix=system_content)
