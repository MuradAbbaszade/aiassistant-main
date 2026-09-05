"""
OpenAI chat responder with Knowledge Base context (RAG-lite).

Uses keyword retrieval from knowledge.services.search, then gpt-* for the reply.
Falls back to MockRAGResponder if the API key is missing or the call fails.
"""
from __future__ import annotations

import json
import logging
import re
from typing import Any

from django.conf import settings

from ai.services.lead_detection import detect_lead_signals, maybe_create_lead
from ai.services.responder import (
    AIResponse,
    MockRAGResponder,
    _items_payload,
    detect_intent,
)
from ai.services.topic_gate import decide_topic
from businesses.models import Business, BusinessType
from knowledge.services.search import search_knowledge
from leads.models import LeadSource

logger = logging.getLogger(__name__)

TONE_HINTS = {
    "friendly": "Dostyana və isti danış; salamlaşma təbii olsun.",
    "professional": "Peşəkar və aydın danış; həddən artıq qeyri-rəsmi olma.",
    "formal": "Rəsmi və hörmətli dil istifadə et.",
    "casual": "Sərbəst, qısa və gündəlik danışıq üslubu.",
}

LENGTH_HINTS = {
    "short": "Cavabı 1–3 qısa cümlə ilə ver.",
    "medium": "Cavabı 2–5 cümlə ilə ver; lazım olsa bir siyahı.",
    "long": "Ətraflı izah et, amma Instagram DM üçün oxunaqlı saxla (max ~1200 simvol).",
}


def _build_system_prompt(business: Business, settings_obj) -> str:
    assistant = (settings_obj.assistant_name if settings_obj else None) or "AI Assistant"
    language = (settings_obj.language if settings_obj else None) or "az"
    tone = (settings_obj.tone if settings_obj else None) or "friendly"
    length = (settings_obj.response_length if settings_obj else None) or "medium"
    rules = (settings_obj.rules if settings_obj else "") or ""

    lang_line = {
        "az": "Əsasən Azərbaycan dilində cavab ver (müştəri başqa dildə yazsa, o dilə uyğunlaş).",
        "en": "Reply primarily in English (match the customer language if they write otherwise).",
        "ru": "Отвечай в основном на русском (подстраивайся под язык клиента).",
    }.get(language, "Match the customer's language; prefer Azerbaijani for this business.")

    areas = ", ".join(business.service_areas or []) or "—"
    hours = business.working_hours or "—"

    parts = [
        f"Sən «{assistant}» — «{business.name}» biznesi üçün Instagram DM AI Assistant-sən.",
        f"Biznes tipi: {business.get_type_display() if hasattr(business, 'get_type_display') else business.type}.",
        f"İş saatları: {hours}.",
        f"Xidmət əraziləri: {areas}.",
        lang_line,
        TONE_HINTS.get(tone, TONE_HINTS["friendly"]),
        LENGTH_HINTS.get(length, LENGTH_HINTS["medium"]),
        "",
        "Qaydalar:",
        "- Yalnız aşağıdakı Knowledge Base kontekstinə və biznes məlumatına əsaslan.",
        "- Kontekstdə cavab yoxdursa, uydurma; dürüst de ki, bilmirsən və insan operatora yönləndir.",
        "- Qiymət/sahə/şərtləri KB-də yoxdursa təxmin etmə.",
        "- Instagram DM üçün qısa, aydın və köməkçi ol.",
        "- Müştəri ad + +994 telefon verəndə təşəkkür et və qeydə alındığını de (sistem lead yaradır).",
        "- Knowledge Base-də və biznes kontekstində olmayan mövzularda (hava, idman, siyaset, "
        "ümumi söhbət, digər şirkətlər və s.) cavab uydurma; qısa de ki, yalnız bu biznes "
        "üzrə kömək edirsən və mövzunu xidmətlərə yönləndir.",
        "- Tibbi diaqnoz, resept və dərman tövsiyəsi VERMƏ; həkimə yönləndir.",
    ]
    if rules.strip():
        parts.append(f"- Əlavə biznes qaydaları: {rules.strip()}")
    if business.type == BusinessType.MEDICAL:
        parts.append(
            "- Bu tibbi klinikadır: yalnız iş saatı, ünvan, xidmət adları və ümumi info; klinik məsləhət yoxdur."
        )
    return "\n".join(parts)


def _format_kb_context(scored) -> str:
    if not scored:
        return "Knowledge Base-də uyğun qeyd tapılmadı."
    blocks: list[str] = []
    for i, s in enumerate(scored[:6], start=1):
        item = s.item
        blocks.append(
            f"[{i}] ({item.type}) {item.title}\n{item.content.strip()}"
        )
    return "\n\n".join(blocks)


def _history_messages(history: list[str] | None) -> list[dict[str, str]]:
    """history is usually alternating customer lines or free text blobs from callers."""
    msgs: list[dict[str, str]] = []
    for line in (history or [])[-8:]:
        text = (line or "").strip()
        if not text:
            continue
        # Callers often pass "Customer: ..." / "AI: ..." or raw customer lines
        lower = text.lower()
        if lower.startswith("ai:") or lower.startswith("assistant:") or lower.startswith("bot:"):
            msgs.append({"role": "assistant", "content": re.sub(r"^(ai|assistant|bot):\s*", "", text, flags=re.I)})
        else:
            content = re.sub(r"^(customer|user|müştəri|musteri):\s*", "", text, flags=re.I)
            msgs.append({"role": "user", "content": content})
    return msgs


def _call_openai(*, system: str, kb: str, history: list[str] | None, message: str) -> dict[str, Any]:
    from openai import OpenAI

    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    model = getattr(settings, "OPENAI_MODEL", "gpt-4o-mini") or "gpt-4o-mini"

    user_blob = (
        "### Knowledge Base\n"
        f"{kb}\n\n"
        "### Current customer message\n"
        f"{message.strip()}\n\n"
        "Respond with a JSON object only, using real values (not placeholders):\n"
        '{"answer":"<reply text>","confidence":0.85,"requires_human":false,'
        '"detected_intent":"service_pricing"}\n'
        "detected_intent must be one of: general_inquiry, service_pricing, working_hours, "
        "service_area, booking, lead_intent, construction_inquiry, property_inquiry, medical_unsafe, other."
    )

    messages: list[dict[str, str]] = [
        {"role": "system", "content": system},
        *_history_messages(history),
        {"role": "user", "content": user_blob},
    ]

    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.4,
        max_tokens=700,
        response_format={"type": "json_object"},
    )
    raw = (completion.choices[0].message.content or "").strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {"answer": raw, "confidence": 0.7, "requires_human": False, "detected_intent": "general_inquiry"}
    return data


class OpenAIResponder:
    """OpenAI + keyword KB retrieval; same interface as MockRAGResponder."""

    def respond(
        self,
        *,
        business: Business,
        message: str,
        history: list[str] | None = None,
        conversation=None,
        source: str = LeadSource.DEMO,
    ) -> AIResponse:
        history = history or []
        if not (getattr(settings, "OPENAI_API_KEY", "") or "").strip():
            logger.warning("OPENAI_API_KEY missing; falling back to MockRAG")
            return MockRAGResponder().respond(
                business=business,
                message=message,
                history=history,
                conversation=conversation,
                source=source,
            )

        settings_obj = getattr(business, "ai_settings", None)
        intent = detect_intent(message, business.type)
        scored = search_knowledge(business.id, message)
        relevant = _items_payload(scored)
        assistant_name = (settings_obj.assistant_name if settings_obj else None) or "AI Assistant"

        topic = decide_topic(
            business_name=business.name,
            assistant_name=assistant_name,
            message=message,
            intent=intent,
            scored=scored,
            history=history,
        )

        # Greeting: canned reply, no OpenAI. Off-topic: silence (no reply, no GPT).
        if topic.reason == "greeting" and topic.canned_answer:
            return AIResponse(
                answer=topic.canned_answer,
                confidence=0.9,
                requires_human=False,
                detected_intent="greeting",
                lead_potential=False,
                relevant_items=relevant,
                lead_created=None,
                should_reply=True,
            )
        if not topic.on_topic:
            return AIResponse(
                answer="",
                confidence=1.0,
                requires_human=False,
                detected_intent="off_topic",
                lead_potential=False,
                relevant_items=relevant,
                lead_created=None,
                should_reply=False,
            )

        # Hard safety for medical before calling the model
        if business.type == BusinessType.MEDICAL and intent == "medical_unsafe":
            answer = (
                "Təəssüf ki, diaqnoz və dərman tövsiyəsi verə bilmirəm. "
                "Sizi klinikanın həkimi ilə əlaqələndirəcəyəm — zəhmət olmasa gözləyin."
            )
            lead_created = None
            lead, detection = maybe_create_lead(
                business_id=business.id,
                message=message,
                intent=intent,
                source=source,
                conversation=conversation,
                history=history,
            )
            if lead and detection.can_create:
                lead_created = {
                    "id": lead.id,
                    "name": lead.name,
                    "contact": lead.contact,
                    "status": lead.status,
                    "intent": lead.intent,
                }
            return AIResponse(
                answer=answer,
                confidence=0.95,
                requires_human=True,
                detected_intent=intent,
                lead_potential=True,
                relevant_items=relevant,
                lead_created=lead_created,
            )

        try:
            data = _call_openai(
                system=_build_system_prompt(business, settings_obj),
                kb=_format_kb_context(scored),
                history=history,
                message=message,
            )
            answer = str(data.get("answer") or "").strip()
            if not answer:
                raise ValueError("Empty OpenAI answer")
            confidence = float(data.get("confidence") or 0.75)
            confidence = max(0.0, min(confidence, 0.99))
            requires_human = bool(data.get("requires_human"))
            model_intent = str(data.get("detected_intent") or intent).strip() or intent
            if model_intent in ("short_snake_case", "string", "intent", "..."):
                model_intent = intent
        except Exception as exc:
            logger.exception("OpenAI call failed; falling back to MockRAG: %s", exc)
            return MockRAGResponder().respond(
                business=business,
                message=message,
                history=history,
                conversation=conversation,
                source=source,
            )

        lead_signals = detect_lead_signals(message, history)
        lead_potential = lead_signals.lead_potential or model_intent in (
            "lead_intent",
            "construction_inquiry",
            "booking",
            "property_inquiry",
            "service_pricing",
        )

        lead_created = None
        lead, detection = maybe_create_lead(
            business_id=business.id,
            message=message,
            intent=model_intent,
            source=source,
            conversation=conversation,
            history=history,
        )
        if detection.lead_potential:
            lead_potential = True
        if lead and detection.can_create:
            lead_created = {
                "id": lead.id,
                "name": lead.name,
                "contact": lead.contact,
                "status": lead.status,
                "intent": lead.intent,
            }
            if lead.name and lead.name not in answer:
                answer += (
                    f"\n\nTəşəkkürlər, {lead.name}! Məlumatlarınız qeydə alındı. "
                    "Komandamız tezliklə sizinlə əlaqə saxlayacaq."
                )
            confidence = max(confidence, 0.9)

        # Instagram hard limit safety
        if len(answer) > 950:
            answer = answer[:947] + "..."

        return AIResponse(
            answer=answer.strip(),
            confidence=round(confidence, 2),
            requires_human=requires_human,
            detected_intent=model_intent,
            lead_potential=lead_potential,
            relevant_items=relevant,
            lead_created=lead_created,
        )
