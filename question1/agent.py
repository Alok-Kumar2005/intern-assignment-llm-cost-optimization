from __future__ import annotations

import json
import re
from dataclasses import dataclass

from shared.billing import CostSession
from shared.kb import article_ids
from shared.llm import ChatMessage, LlmClient
from shared.tools import format_thread, get_order, get_ticket


@dataclass
class TicketResolution:
    action: str
    kb_article: str
    customer_reply: str
    raw_completion: str


def parse_resolution(text: str) -> TicketResolution:
    m = re.search(r"\{[\s\S]*\}", text)
    if not m:
        raise ValueError(f"No JSON in model output:\n{text[:400]}")
    data = json.loads(m.group())
    return TicketResolution(
        action=str(data["action"]).upper(),
        kb_article=str(data["kb_article"]),
        customer_reply=str(data.get("customer_reply", "")),
        raw_completion=text,
    )


# Compressed KB - just the essential facts
_COMPACT_KB = """returns-within-30-days: Physical items, resalable condition, refund within 30 days of delivery
digital-license-no-refund: Digital products not refundable after license/download revealed
custom-items-no-replace: Custom/personalized items not eligible for auto replacement, escalate to Tier 2
damage-replacement-7-days: Standard catalog items damaged within 7 days qualify for free replacement
subscription-cooling-off: Annual subscriptions get prorated refund if cancelled within 30 days"""

# Minimal examples
_FEW_SHOT = """Examples:
physical,!opened,≤30d→{"action":"REFUND","kb_article":"returns-within-30-days"}
digital,revealed→{"action":"SEND_ARTICLE","kb_article":"digital-license-no-refund"}
custom,damaged→{"action":"ESCALATE_TIER2","kb_article":"custom-items-no-replace"}
catalog,damaged,≤7d→{"action":"REPLACE","kb_article":"damage-replacement-7-days"}"""


class SupportCopilot:
    """
    ShopAssist Tier-1 copilot (optimized).

    Given a support ticket + order snapshot, choose an action, cite the help-center
    article, and draft the customer reply.
    """

    def __init__(self, session: CostSession | None = None):
        self.session = session or CostSession()
        self.llm = LlmClient(self.session)

    def build_messages(self, ticket_id: str) -> list[ChatMessage]:
        ticket = get_ticket(ticket_id)
        order = get_order(ticket["order_id"])
        thread = format_thread(ticket)
        snapshot = json.dumps(order, indent=2)

        # Stable system prompt for caching (no UUID)
        system = "\n\n".join(
            [
                "ShopAssist Tier-1 support copilot.",
                _FEW_SHOT,
                f"KB:\n{_COMPACT_KB}",
                'Output JSON only: {"action":"<ACTION>","kb_article":"<article-id>","customer_reply":"<reply>"}',
            ]
        )
        user = "\n\n".join(
            [
                f"TICKET: {ticket_id}",
                f"THREAD:\n{thread}",
                f"ORDER_SNAPSHOT:\n{snapshot}\nEND_SNAPSHOT",
            ]
        )
        return [ChatMessage("system", system), ChatMessage("user", user)]

    def handle_ticket(self, ticket_id: str) -> TicketResolution:
        messages = self.build_messages(ticket_id)
        
        # Enable caching on the system message
        system_content = messages[0].content
        
        completion = self.llm.chat(
            "handle_ticket", 
            messages,
            cached_prefix=system_content
        )
        return parse_resolution(completion)
