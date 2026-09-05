import re
import unicodedata
from typing import Iterable


AZ_MAP = str.maketrans(
    {
        "ə": "e",
        "ı": "i",
        "ö": "o",
        "ü": "u",
        "ş": "s",
        "ç": "c",
        "ğ": "g",
        "Ə": "e",
        "I": "i",
        "İ": "i",
        "Ö": "o",
        "Ü": "u",
        "Ş": "s",
        "Ç": "c",
        "Ğ": "g",
    }
)


def normalize_az(text: str) -> str:
    """Normalize Azerbaijani text for keyword matching."""
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", text)
    text = text.translate(AZ_MAP).lower()
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize(text: str) -> list[str]:
    norm = normalize_az(text)
    return [t for t in re.split(r"[^\w]+", norm) if t and len(t) > 1]


def format_azn(amount: float | int) -> str:
    """Format money in az-AZ style: 160.000 AZN"""
    n = int(round(amount))
    s = f"{n:,}".replace(",", ".")
    return f"{s} AZN"


def extract_square_meters(text: str) -> float | None:
    """Extract m² value from text like '200 m²', '200m2', '200 kvadrat'."""
    norm = normalize_az(text)
    patterns = [
        r"(\d+[.,]?\d*)\s*(?:m2|m²|kv\.?\s*m|kvadrat)",
        r"(\d+[.,]?\d*)\s*m\s*2",
    ]
    for pat in patterns:
        m = re.search(pat, norm)
        if m:
            return float(m.group(1).replace(",", "."))
    return None


def extract_phone_994(text: str) -> str | None:
    """Extract +994 phone numbers."""
    m = re.search(r"(\+994[\s\-]?\d{2}[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2})", text)
    if m:
        digits = re.sub(r"[^\d+]", "", m.group(1))
        if digits.startswith("+"):
            return "+994 " + " ".join(
                [digits[4:6], digits[6:9], digits[9:11], digits[11:13]]
            ).strip()
        return m.group(1)
    # looser: 994 XX XXX XX XX
    m2 = re.search(r"(994[\s\-]?\d{2}[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2})", text)
    if m2:
        raw = re.sub(r"[^\d]", "", m2.group(1))
        return f"+{raw[:3]} {raw[3:5]} {raw[5:8]} {raw[8:10]} {raw[10:12]}"
    return None


def extract_az_full_name(text: str) -> str | None:
    """
    Detect Azerbaijani-style full name: two capitalized words (Latin + AZ letters).
    Examples: Aysel Məmmədova, Elvin Quliyev
    """
    pattern = re.compile(
        r"\b([A-ZƏÖÜĞÇŞİ][a-zəöüğçşı]+)\s+([A-ZƏÖÜĞÇŞİ][a-zəöüğçşı]+)\b"
    )
    m = pattern.search(text)
    if m:
        return f"{m.group(1)} {m.group(2)}"
    return None


def contains_any(text: str, needles: Iterable[str]) -> bool:
    norm = normalize_az(text)
    return any(normalize_az(n) in norm for n in needles)
