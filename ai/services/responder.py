"""
Mock RAG AI responder (v1).

Pipeline:
1. Normalize Azerbaijani text
2. Keyword search KnowledgeItem
3. Detect intent
4. Business-type handlers
5. Lead potential / create when name + +994 phone
6. Return structured AIResponse

Set AI_PROVIDER=openai + OPENAI_API_KEY to use OpenAI (see openai_responder.py).
"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any, Protocol

from ai.services.lead_detection import detect_lead_signals, maybe_create_lead
from businesses.models import Business, BusinessType
from core.utils import (
    contains_any,
    extract_az_full_name,
    extract_phone_994,
    extract_square_meters,
    format_azn,
    normalize_az,
)
from knowledge.models import KnowledgeItem, KnowledgeType
from knowledge.services.search import get_best_service_price_item, search_knowledge
from leads.models import LeadSource


@dataclass
class AIResponse:
    answer: str
    confidence: float
    requires_human: bool
    detected_intent: str
    lead_potential: bool
    relevant_items: list[dict[str, Any]] = field(default_factory=list)
    lead_created: dict[str, Any] | None = None
    should_reply: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class AIResponder(Protocol):
    def respond(
        self,
        *,
        business: Business,
        message: str,
        history: list[str] | None = None,
        conversation=None,
        source: str = LeadSource.DEMO,
    ) -> AIResponse: ...


INTENT_KEYWORDS: dict[str, tuple[str, ...]] = {
    "medical_unsafe": (
        "diaqnoz",
        "diagnosis",
        "recipt",
        "resept",
        "derman",
        "dərman",
        "ilac",
        "ilaç",
        "doza",
        "antibiotik",
        "mualice et",
        "müalicə et",
        "hansı dərman",
        "hansi derman",
    ),
    "service_pricing": ("qiymet", "neceye", "neçəyə", "nece olacaq", "hesabla", "tarif", "bahali"),
    "working_hours": ("is saat", "iş saat", "ne vaxt aciq", "ne vaxta qeder", "working hours"),
    "service_area": ("xirdalan", "sumqayit", "baki", "erazi", "ərazi", "harada isleyir", "qebale", "qəbələ"),
    "booking": ("rezerv", "bron", "masa", "rezervasiya", "gorus", "görüş", "randevu"),
    "property_inquiry": ("menzil", "kiraye", "satilir", "otaq", "emlak", "əmlak", "ev al"),
    "construction_inquiry": ("tik", "ev tik", "villa", "temir", "təmir", "fasad", "insaat", "inşaat"),
    "lead_intent": ("baslamaq", "muraciet", "elaqe", "zeng edin", "isteyirem basla"),
}


def detect_intent(message: str, business_type: str) -> str:
    norm = normalize_az(message)

    if business_type == BusinessType.MEDICAL and contains_any(message, INTENT_KEYWORDS["medical_unsafe"]):
        return "medical_unsafe"

    scores: dict[str, int] = {}
    for intent, kws in INTENT_KEYWORDS.items():
        if intent == "medical_unsafe":
            continue
        scores[intent] = sum(1 for k in kws if normalize_az(k) in norm)

    # Boost by business type
    if business_type == BusinessType.CONSTRUCTION:
        scores["construction_inquiry"] = scores.get("construction_inquiry", 0) + 1
        if extract_square_meters(message):
            scores["construction_inquiry"] = scores.get("construction_inquiry", 0) + 2
            scores["service_pricing"] = scores.get("service_pricing", 0) + 1
    elif business_type == BusinessType.RESTAURANT:
        scores["booking"] = scores.get("booking", 0) + 1
    elif business_type == BusinessType.REAL_ESTATE:
        scores["property_inquiry"] = scores.get("property_inquiry", 0) + 1

    best = max(scores, key=scores.get) if scores else "general_inquiry"
    if scores.get(best, 0) <= 0:
        return "general_inquiry"
    return best


def parse_azn_per_m2(text: str) -> float | None:
    """
    Parse price like '800 AZN/m²' from service content.
    NEVER pick unrelated numbers (e.g. 200 from FAQ about 200 m²).
    """
    patterns = [
        r"(\d+[.,]?\d*)\s*azn\s*/\s*m",
        r"(\d+[.,]?\d*)\s*azn\s*/\s*kv",
        r"(\d+[.,]?\d*)\s*azn\s*m2",
        r"azn\s*/\s*m[²2]?\s*[:\-]?\s*(\d+[.,]?\d*)",
    ]
    n = normalize_az(text)
    for pat in patterns:
        m = re.search(pat, n)
        if m:
            return float(m.group(1).replace(",", "."))
    # Fallback: "Ev tikintisi 800 AZN/m²" style — number immediately before AZN/m
    m = re.search(r"(\d{2,5})\s*azn\s*/\s*m", n)
    if m:
        return float(m.group(1))
    return None


def _items_payload(scored) -> list[dict[str, Any]]:
    return [
        {
            "id": s.item.id,
            "title": s.item.title,
            "type": s.item.type,
            "score": round(s.score, 2),
            "content": s.item.content[:280],
        }
        for s in scored
    ]


class MockRAGResponder:
    """Keyword RAG + business-type handlers."""

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
        settings_obj = getattr(business, "ai_settings", None)
        btype = business.type
        intent = detect_intent(message, btype)
        scored = search_knowledge(business.id, message)
        relevant = _items_payload(scored)

        lead_signals = detect_lead_signals(message, history)
        lead_potential = lead_signals.lead_potential or intent in (
            "lead_intent",
            "construction_inquiry",
            "booking",
            "property_inquiry",
        )

        requires_human = False
        confidence = 0.72
        answer = ""

        if btype == BusinessType.MEDICAL and intent == "medical_unsafe":
            requires_human = True
            confidence = 0.95
            answer = (
                "Təəssüf ki, diaqnoz və dərman tövsiyəsi verə bilmirəm. "
                "Sizi klinikanın həkimi ilə əlaqələndirəcəyəm — zəhmət olmasa gözləyin."
            )
            if settings_obj and settings_obj.rules:
                answer += "\n\n(Qayda: tibbi məsləhət / resept verilmir.)"
        elif btype == BusinessType.CONSTRUCTION:
            answer, confidence, requires_human = self._handle_construction(
                business, message, intent, scored, history
            )
        elif btype == BusinessType.RESTAURANT:
            answer, confidence, requires_human = self._handle_restaurant(
                business, message, intent, scored, history
            )
        elif btype == BusinessType.REAL_ESTATE:
            answer, confidence, requires_human = self._handle_real_estate(
                business, message, intent, scored, history
            )
        else:
            answer, confidence = self._generic_from_kb(business, message, scored)

        lead_created = None
        lead, detection = maybe_create_lead(
            business_id=business.id,
            message=message,
            intent=intent,
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
            answer += (
                f"\n\nTəşəkkürlər, {lead.name}! Məlumatlarınız qeydə alındı. "
                "Komandamız tezliklə sizinlə əlaqə saxlayacaq."
            )
            confidence = max(confidence, 0.9)

        if settings_obj and settings_obj.assistant_name and intent == "general_inquiry" and not scored:
            answer = answer or f"Salam! Mən {settings_obj.assistant_name}. Necə kömək edə bilərəm?"

        return AIResponse(
            answer=answer.strip(),
            confidence=round(min(confidence, 0.99), 2),
            requires_human=requires_human,
            detected_intent=intent,
            lead_potential=lead_potential,
            relevant_items=relevant,
            lead_created=lead_created,
        )

    def _handle_construction(self, business, message, intent, scored, history):
        norm = normalize_az(message)
        m2 = extract_square_meters(message)
        areas = [normalize_az(a) for a in (business.service_areas or [])]
        # Area check FIRST (before greeting)
        area_asked = any(
            x in norm
            for x in (
                "xirdalan",
                "sumqayit",
                "baki",
                "qebele",
                "qebale",
                "qabala",
                "harada",
                "erazi",
            )
        )
        # ə→e maps Qəbələ → qebele (also accept qebale/qabala spellings)
        qabala = any(x in norm for x in ("qebele", "qebale", "qabala", "gabala"))

        if qabala:
            conf = 0.88
            ans = (
                "Hazırda əsas xidmət ərazilərimiz Bakı, Xırdalan və Sumqayıtdır. "
                "Qəbələ üzrə layihələr fərdi qiymətləndirmə tələb edir — "
                "sizi menecerimizə yönləndirə bilərik."
            )
            return ans, conf, True

        parts: list[str] = []
        conf = 0.75
        requires_human = False
        hist_blob = normalize_az(" ".join(history or []))
        m2_current = m2
        # History m² only for follow-up pricing ("Qiymət neçəyə?")
        m2_hist = extract_square_meters(" ".join(history or [])) if m2 is None else None

        if extract_az_full_name(message) and extract_phone_994(message):
            return (
                "Məlumatlarınızı aldım.",
                0.92,
                False,
            )

        if area_asked or "xirdalan" in norm:
            if "xirdalan" in norm:
                parts.append("Bəli, Xırdalanda işləyirik.")
                conf = 0.93
            elif areas:
                parts.append(
                    "Xidmət ərazilərimiz: " + ", ".join(business.service_areas) + "."
                )
                conf = 0.9

        wants_price = intent == "service_pricing" or any(
            x in norm for x in ("qiymet", "neceye", "nece olacaq", "hesabla")
        )
        villa = "villa" in norm or (wants_price and "villa" in hist_blob)
        temir = "temir" in norm
        fasad = "fasad" in norm
        lead_ask = intent == "lead_intent" or "baslamaq" in norm

        # Pure "başlamaq" on this turn → ask for contact (ignore history m²)
        if lead_ask and not (m2_current or wants_price or "villa" in norm or temir or fasad):
            parts.append(
                "Əla! Başlamaq üçün ad, soyad və +994 ilə telefon nömrənizi yazın — "
                "sizi potensial müştəri kimi qeydə alaq."
            )
            conf = 0.9
            if normalize_az(message).startswith("salam") and parts:
                return "Salam! " + " ".join(parts), conf, requires_human
            return " ".join(parts), conf, requires_human

        if wants_price and m2 is None and m2_hist is not None:
            m2 = m2_hist

        if m2 or wants_price or villa or temir or fasad or (
            intent == "construction_inquiry" and not lead_ask
        ):
            query_for_price = message
            if villa:
                query_for_price = "villa tikinti qiymet AZN/m2"
            elif temir:
                query_for_price = "temir qiymet AZN"
            elif fasad:
                query_for_price = "fasad qiymet AZN"
            elif m2 or "ev" in norm or "ev" in hist_blob:
                query_for_price = "ev tikintisi qiymet AZN/m2"

            price_item = get_best_service_price_item(business.id, query_for_price)
            # Also try direct service lookup by keywords
            if villa:
                price_item = (
                    KnowledgeItem.objects.filter(
                        business=business, type=KnowledgeType.SERVICE, title__icontains="Villa"
                    ).first()
                    or price_item
                )
            elif temir:
                price_item = (
                    KnowledgeItem.objects.filter(
                        business=business, type=KnowledgeType.SERVICE, title__icontains="Təmir"
                    ).first()
                    or KnowledgeItem.objects.filter(
                        business=business, type=KnowledgeType.SERVICE, title__icontains="Temir"
                    ).first()
                    or price_item
                )
            elif fasad:
                price_item = (
                    KnowledgeItem.objects.filter(
                        business=business, type=KnowledgeType.SERVICE, title__icontains="Fasad"
                    ).first()
                    or price_item
                )
            else:
                price_item = (
                    KnowledgeItem.objects.filter(
                        business=business, type=KnowledgeType.SERVICE, title__icontains="Ev tikintisi"
                    ).first()
                    or price_item
                )

            rate = parse_azn_per_m2(price_item.content + " " + price_item.title) if price_item else None
            # Flat prices for temir/fasad without m2 rate
            if rate is None and price_item:
                flat = re.search(r"(\d+[.,]?\d*)\s*azn", normalize_az(price_item.content))
                if flat and not m2:
                    parts.append(price_item.content.strip())
                    conf = max(conf, 0.9)
                elif flat and m2:
                    # temir/fasad often per m2 too
                    val = float(flat.group(1).replace(",", "."))
                    # Only use if content suggests per m2
                    blob = normalize_az(price_item.content)
                    if "m2" in blob or "/m" in blob:
                        rate = val

            if m2 and rate:
                total = m2 * rate
                label = "villa" if villa else "ev tikintisi"
                parts.append(
                    f"{int(m2)} m² {label} üçün təxmini qiymət: "
                    f"{format_azn(total)} ({format_azn(rate)}/m² × {int(m2)} m²)."
                )
                conf = max(conf, 0.94)
            elif rate and wants_price:
                parts.append(f"Baza qiymətimiz təxminən {format_azn(rate)}/m²-dir. Sahəni deyin, dəqiq hesablayaq.")
                conf = max(conf, 0.88)
            elif price_item and not any(price_item.content[:40] in p for p in parts):
                parts.append(price_item.content.strip())
                conf = max(conf, 0.85)

        if lead_ask:
            parts.append(
                "Əla! Başlamaq üçün ad, soyad və +994 ilə telefon nömrənizi yazın — "
                "sizi potensial müştəri kimi qeydə alaq."
            )
            conf = max(conf, 0.9)

        if intent == "working_hours" or "saat" in norm:
            if business.working_hours:
                parts.append(f"İş saatlarımız: {business.working_hours}.")
                conf = max(conf, 0.9)

        # Payment / warranty FAQs from KB
        if any(x in norm for x in ("odenis", "odeme", "pul", "zemanet", "muddet", "ne qeder vaxt")):
            if scored:
                parts.append(scored[0].item.content.strip())
                conf = max(conf, 0.87)

        if not parts:
            answer, conf2 = self._generic_from_kb(business, message, scored)
            return answer, conf2, False

        # Soft greeting only as prefix if message starts with Salam AND we have substance
        if normalize_az(message).startswith("salam") and parts:
            return "Salam! " + " ".join(parts), conf, requires_human
        return " ".join(parts), conf, requires_human

    def _handle_restaurant(self, business, message, intent, scored, history):
        norm = normalize_az(message)
        hist = normalize_az(" ".join(history))
        conf = 0.8
        requires_human = False

        if intent == "booking" or any(x in norm for x in ("rezerv", "bron", "masa")):
            has_date = bool(re.search(r"\d{1,2}[./]\d{1,2}|\b(bazar|duyen|cersenbe|cume|sabah)\b", norm))
            has_time = bool(re.search(r"\d{1,2}[:.]\d{2}|\b\d{1,2}\s*(am|pm)?\b", norm))
            has_guests = bool(re.search(r"\d+\s*(nefer|nəfər|kisi|adam|guest)", norm))
            missing = []
            if not has_date and "tarix" not in hist:
                missing.append("tarix")
            if not has_time:
                missing.append("saat")
            if not has_guests:
                missing.append("qonaq sayı")
            if missing:
                return (
                    "Əlbəttə, rezervasiya edək! Zəhmət olmasa "
                    + ", ".join(missing)
                    + " deyin.",
                    0.86,
                    False,
                )
            return (
                "Rezervasiya sorğunuz qəbul olundu. Təsdiq üçün komandamız əlaqə saxlayacaq.",
                0.9,
                False,
            )

        if scored:
            return scored[0].item.content.strip(), 0.82, False
        cuisine = ", ".join(business.cuisine or []) or "müxtəlif mətbəx"
        return (
            f"Urban Table — {cuisine}. Rezervasiya və ya menyu haqqında sualınız varsa yazın!",
            0.7,
            False,
        )

    def _handle_real_estate(self, business, message, intent, scored, history):
        norm = normalize_az(message)
        if intent == "property_inquiry" or any(x in norm for x in ("menzil", "kiraye", "satilir", "otaq")):
            missing = []
            if not any(x in norm for x in ("otaq", "1", "2", "3", "4")):
                missing.append("otaq sayı")
            if not any(x in norm for x in ("kiraye", "satın", "satinal", "almaq", "satilir")):
                missing.append("kirayə / satış")
            if not any(x in norm for x in ("baki", "rayon", "nesimi", "nerimanov", "yasamal", "xetai")):
                missing.append("rayon / ərazi")
            if missing and len(missing) >= 2:
                return (
                    "Sizə uyğun əmlak tapa bilərik. Zəhmət olmasa "
                    + ", ".join(missing)
                    + " deyin.",
                    0.84,
                    False,
                )
            if scored:
                return scored[0].item.content.strip() + " Əlavə detal üçün mütəxəssisimizə yönləndirə bilərik.", 0.88, False
            return "Uyğun variantları hazırlayıb göndərəcəyik. Büdcənizi də yaza bilərsiniz.", 0.8, False
        if scored:
            return scored[0].item.content.strip(), 0.8, False
        return "Prime Estate — daşınmaz əmlak üzrə köməkçi. Axtardığınız əmlakı təsvir edin.", 0.68, False

    def _generic_from_kb(self, business, message, scored):
        if scored:
            top = scored[0].item
            # Never return greeting FAQ alone if message has substance — already filtered
            return top.content.strip(), min(0.55 + scored[0].score / 20.0, 0.92)
        name = business.name
        return (
            f"Salam! {name} üçün AI köməkçisiyəm. Sualınızı bir az ətraflı yazın, "
            "Knowledge Base-ə əsasən cavab verəcəyəm.",
            0.55,
        )


def get_responder() -> AIResponder:
    from django.conf import settings

    provider = (getattr(settings, "AI_PROVIDER", "mock") or "mock").strip().lower()
    if provider == "openai":
        from ai.services.openai_responder import OpenAIResponder

        return OpenAIResponder()
    return MockRAGResponder()
