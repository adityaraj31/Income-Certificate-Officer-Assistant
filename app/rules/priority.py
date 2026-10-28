from typing import List
from app.rules.flag import Flag


SEV = {"low": 1, "medium": 2, "high": 3, "critical": 4}


def score_application(flags: List[Flag], days_left: int = 0) -> int:
    base = 0
    for f in flags:
        base += SEV.get(f.severity, 1) * 10
    # SLA urgency
    if days_left < 0:
        base += 50  # past due
    elif days_left <= 2:
        base += 30
    elif days_left <= 5:
        base += 15
    # age factor small
    if days_left < 0:
        base += abs(days_left) * 2
    return base


def priority_level(score: int) -> str:
    if score >= 100:
        return "अति प्राथमिक"
    if score >= 60:
        return "उच्च प्राथमिकता"
    if score >= 30:
        return "मध्यम प्राथमिकता"
    return "सामान्य"
