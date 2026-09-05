"""
Topic gate: decide if a DM is business-related before calling OpenAI.

Unrelated messages get a fixed refusal — no GPT request.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from core.utils import extract_az_full_name, extract_phone_994, normalize_az
from knowledge.services.search import ScoredItem

# Minimum keyword-RAG score to treat KB as supporting the question
MIN_KB_SCORE = 4.0

ON_TOPIC_INTENTS = frozenset(
    {
        "service_pricing",
        "working_hours",
        "service_area",
        "booking",
        "lead_intent",
        "construction_inquiry",
        "property_inquiry",
        "medical_unsafe",
    }
)

GREETING_ONLY = re.compile(
    r"^(salam|salamlar|hello|hi|hey|necesen|necesiniz|"
    r"sabahiniz xeyir|axsaminiz xeyir|gunortaniz xeyir)[\s!.?]*$",
    re.I,
)

# Short follow-ups after an on-topic thread (allow GPT without strong KB hit)
FOLLOW_UP = re.compile(
    r"^(beli|bəli|xeyr|he|hə|ok|okay|super|tesekkur|təşəkkür|sagol|sağol|"
    r"neceye|neçəyə|nece|neçə|daha|etrafli|ətraflı|basqa|başqa|"
    r"yeni|ve|və|niye|niyə|harda|harada|ne vaxt|nə vaxt)[\w\s!.?]{0,40}$",
    re.I,
)

GREETING_REPLY = (
    "Hi! I'm {assistant} — the AI helper for {business}. "
    "Ask about pricing, services, or how to get in touch."
)


@dataclass
class TopicDecision:
    on_topic: bool
    reason: str
    canned_answer: str | None = None


def _is_greeting_only(message: str) -> bool:
    return bool(GREETING_ONLY.match(normalize_az(message).strip()))


def _is_short_follow_up(message: str, history: list[str] | None) -> bool:
    if not history:
        return False
    return bool(FOLLOW_UP.match(normalize_az(message).strip()))


def decide_topic(
    *,
    business_name: str,
    assistant_name: str,
    message: str,
    intent: str,
    scored: list[ScoredItem],
    history: list[str] | None = None,
) -> TopicDecision:
    history = history or []
    top = scored[0].score if scored else 0.0

    if _is_greeting_only(message):
        return TopicDecision(
            on_topic=True,
            reason="greeting",
            canned_answer=GREETING_REPLY.format(
                assistant=assistant_name or "AI Assistant",
                business=business_name,
            ),
        )

    # Contact capture — always handle without needing KB
    if extract_az_full_name(message) or extract_phone_994(message):
        return TopicDecision(on_topic=True, reason="contact_info")

    if intent in ON_TOPIC_INTENTS:
        return TopicDecision(on_topic=True, reason=f"intent:{intent}")

    if top >= MIN_KB_SCORE:
        return TopicDecision(on_topic=True, reason=f"kb:{top:.1f}")

    if _is_short_follow_up(message, history):
        return TopicDecision(on_topic=True, reason="follow_up")

    return TopicDecision(
        on_topic=False,
        reason="off_topic",
        canned_answer=None,
    )
