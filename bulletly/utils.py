import re
from pathlib import Path
from typing import List

BANNED_WORDS = {"synergy", "rockstar", "guru", "world-class"}
STRONG_VERBS = ["created", "built", "implemented", "automated", "optimized", "reduced", "delivered", "designed", "led"]
TECH_KEYWORDS = ["python", "sql", "spark", "airflow", "kafka", "aws", "gcp", "docker", "kubernetes"]


def extract_numbers(s: str) -> List[str]:
    return re.findall(r"\d[\d,\.]*", s)


def has_numbers(s: str) -> bool:
    return bool(extract_numbers(s))


def contains_banned_word(s: str) -> List[str]:
    found = [w for w in BANNED_WORDS if w.lower() in s.lower()]
    return found


def anonymize_sensitive(s: str) -> str:
    # very simple anonymization: emails, domains, phone numbers, and sequences of caps
    s = re.sub(r"[\w\.-]+@[\w\.-]+", "[redacted_email]", s)
    s = re.sub(r"\bhttps?://[\w\./-]+\b", "[redacted_url]", s)
    s = re.sub(r"\+?\d[\d \-]{6,}\d", "[redacted_phone]", s)
    # redact sequences of two or more capitalized words (possible client names)
    s = re.sub(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b", "[redacted_company]", s)
    return s


def read_bullets_from_file(p: Path) -> List[str]:
    text = p.read_text(encoding="utf8")
    return [line.strip() for line in text.splitlines() if line.strip()]


def save_json(p: Path, obj):
    import json

    p.write_text(json.dumps(obj, indent=2), encoding="utf8")


def detect_tech_words(s: str) -> List[str]:
    return [t for t in TECH_KEYWORDS if t.lower() in s.lower()]


def quick_critique(s: str) -> str:
    reasons = []
    if not re.search(r"\b(led|built|created|implemented|designed|delivered|reduced|optimized|automated)\b", s, re.I):
        reasons.append("vague or weak verb")
    if len(s.split()) < 5:
        reasons.append("missing scope or outcome")
    if len(s) > 200:
        reasons.append("long and unfocused")
    return ", ".join(reasons) if reasons else "concise and specific"


def needs_clarifying_questions(s: str) -> bool:
    crit = quick_critique(s)
    return "missing scope" in crit or "missing scope or outcome" in crit or not re.search(r"\b(by|with|leading to|resulting in|resulted in)\b", s, re.I)
