"""
Keyword search over KnowledgeItem for a business (mock RAG retrieval).
Swap this module for embedding similarity later without changing views.
"""
from __future__ import annotations

from dataclasses import dataclass

from core.utils import normalize_az, tokenize
from knowledge.models import KnowledgeItem, KnowledgeType


@dataclass
class ScoredItem:
    item: KnowledgeItem
    score: float


GREETING_MARKERS = (
    "salam",
    "xos gelmisiniz",
    "xosgeldiniz",
    "greeting",
    "salamlama",
)


def _is_greeting_item(item: KnowledgeItem) -> bool:
    blob = normalize_az(f"{item.title} {item.content} {' '.join(item.keywords or [])}")
    return any(m in blob for m in GREETING_MARKERS) and item.type == KnowledgeType.FAQ


def _score_item(query: str, item: KnowledgeItem) -> float:
    q_tokens = set(tokenize(query))
    if not q_tokens:
        return 0.0

    title_n = normalize_az(item.title)
    content_n = normalize_az(item.content)
    kw_n = normalize_az(" ".join(item.keywords or []))

    title_tokens = set(tokenize(item.title))
    content_tokens = set(tokenize(item.content))
    kw_tokens = set(tokenize(" ".join(item.keywords or [])))

    score = 0.0
    for token in q_tokens:
        if len(token) < 3:
            continue
        if token in title_n:
            score += 4.0
        if token in kw_n:
            score += 3.5
        if token in content_n:
            score += 1.5

    score += (
        len(q_tokens & title_tokens) * 3.0
        + len(q_tokens & kw_tokens) * 2.5
        + len(q_tokens & content_tokens) * 1.0
    )

    if item.type == KnowledgeType.SERVICE:
        score *= 1.25
    elif item.type == KnowledgeType.BUSINESS:
        score *= 1.1
    elif item.type == KnowledgeType.POLICY:
        score *= 1.05

    qn = normalize_az(query)
    if "xirdalan" in qn and "xirdalan" in (title_n + " " + content_n + " " + kw_n):
        score += 8.0
    if any(x in qn for x in ("qiymet", "neceye", "nece olacaq", "hesabla")):
        if any(x in (title_n + content_n + kw_n) for x in ("qiymet", "azn", "m2", "kvadrat")):
            score += 5.0
    if any(x in qn for x in ("qebele", "qebale", "qabala")):
        if any(x in (title_n + content_n + kw_n) for x in ("qebele", "qebale", "qabala", "qəbələ")):
            score += 6.0
    if "zemanet" in qn or "garant" in qn:
        if "zemanet" in (title_n + content_n) or "garant" in (title_n + content_n):
            score += 5.0
    if "odenis" in qn or "pul" in qn or "odeme" in qn:
        if any(x in (title_n + content_n) for x in ("odenis", "odeme", "pul")):
            score += 5.0

    return score


def search_knowledge(
    business_id: str,
    query: str,
    *,
    limit: int = 8,
    exclude_greeting_if_substantive: bool = True,
) -> list[ScoredItem]:
    items = list(KnowledgeItem.objects.filter(business_id=business_id))
    scored: list[ScoredItem] = []
    for item in items:
        s = _score_item(query, item)
        if s > 0:
            scored.append(ScoredItem(item=item, score=s))

    scored.sort(key=lambda x: x.score, reverse=True)

    qn = normalize_az(query)
    remainder = qn
    for g in ("salam", "necesen", "necesiniz", "sabahiniz xeyir", "axsaminiz xeyir"):
        if remainder.startswith(g):
            remainder = remainder[len(g) :].strip(" ,!.?")
            break

    is_substantive = len(remainder) > 8 or any(
        k in qn
        for k in (
            "m2",
            "ev",
            "villa",
            "tik",
            "qiymet",
            "xirdalan",
            "temir",
            "fasad",
            "qebale",
            "baslamaq",
            "isteyirem",
            "rezerv",
            "hekim",
            "mualice",
            "kiraye",
            "menzil",
        )
    )

    if exclude_greeting_if_substantive and is_substantive:
        filtered = [s for s in scored if not _is_greeting_item(s.item)]
        if filtered:
            scored = filtered

    return scored[:limit]


def get_best_service_price_item(business_id: str, query: str) -> KnowledgeItem | None:
    results = search_knowledge(business_id, query, limit=15, exclude_greeting_if_substantive=True)
    service_hits = [r for r in results if r.item.type == KnowledgeType.SERVICE]
    if service_hits:
        for r in service_hits:
            blob = normalize_az(r.item.content + " " + r.item.title)
            if "azn" in blob and ("m2" in blob or "m²" in r.item.content.lower()):
                return r.item
        return service_hits[0].item
    for r in results:
        blob = normalize_az(r.item.content + " " + r.item.title)
        if "azn" in blob and ("m2" in blob or "/m" in blob):
            return r.item
    return None
