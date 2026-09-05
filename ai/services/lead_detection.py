"""Lead potential scoring and creation rules."""
from __future__ import annotations

import re
from dataclasses import dataclass

from core.utils import contains_any, extract_az_full_name, extract_phone_994, normalize_az
from leads.models import Lead, LeadSource, LeadStatus


LEAD_POTENTIAL_PATTERNS = (
    "baslamaq",
    "baslayaq",
    "muraciet",
    "müraciət",
    "tikmek",
    "tikmək",
    "tikmək istəyirəm",
    "isteyirem",
    "istəyirəm",
    "elaqe",
    "əlaqə",
    "elaqe saxlayin",
    "zeng edin",
    "zəng edin",
    "bron",
    "rezerv",
    "satinalmaq",
    "almaq istəyirəm",
    "qiymet teklifi",
    "gorus",
    "görüş",
)


@dataclass
class LeadDetectionResult:
    lead_potential: bool
    name: str | None = None
    phone: str | None = None
    can_create: bool = False


def detect_lead_signals(message: str, history: list[str] | None = None) -> LeadDetectionResult:
    history = history or []
    combined = " ".join([*history, message])

    has_m2 = bool(re.search(r"\d+\s*(?:m2|m²|kvadrat)", normalize_az(message)))
    potential = contains_any(combined, LEAD_POTENTIAL_PATTERNS) or has_m2

    name_in_msg = extract_az_full_name(message)
    phone_in_msg = extract_phone_994(message)
    name = name_in_msg or extract_az_full_name(combined)
    phone = phone_in_msg or extract_phone_994(combined)

    # Create only when BOTH are known AND current message contributes name and/or phone
    pair_ready = bool(name and phone)
    contributed = bool(name_in_msg or phone_in_msg)
    can_create = pair_ready and contributed

    if can_create or pair_ready:
        potential = True

    return LeadDetectionResult(
        lead_potential=potential,
        name=name,
        phone=phone,
        can_create=can_create,
    )


def maybe_create_lead(
    *,
    business_id: str,
    message: str,
    intent: str,
    source: str = LeadSource.DEMO,
    conversation=None,
    history: list[str] | None = None,
) -> tuple[Lead | None, LeadDetectionResult]:
    detection = detect_lead_signals(message, history)
    if not detection.can_create:
        return None, detection

    phone_digits = re.sub(r"[^\d]", "", detection.phone or "")
    existing = (
        Lead.objects.filter(business_id=business_id, name__iexact=detection.name or "")
        .filter(contact__icontains=phone_digits[-9:] if len(phone_digits) >= 9 else phone_digits)
        .first()
    )
    if existing:
        # Already logged — do not treat as a new lead toast
        detection.can_create = False
        return None, detection

    lead = Lead.objects.create(
        business_id=business_id,
        name=detection.name or "Naməlum",
        contact=detection.phone or "",
        intent=intent or "Ümumi maraq",
        source=source,
        status=LeadStatus.NEW,
        conversation=conversation,
    )
    return lead, detection
