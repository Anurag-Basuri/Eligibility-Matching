import re

AGE_PATTERNS = [
    r"\b\d{1,3}-year-old\b",
    r"\baged\s+\d{1,3}\b",
    r"\b\d{1,3}\s+years?\s+old\b"
]

def anonymize(text: str) -> str:
    text = re.sub(r"\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b", "PATIENT_NAME", text)
    for pat in AGE_PATTERNS:
        text = re.sub(pat, "AGE", text, flags=re.IGNORECASE)
    return text
