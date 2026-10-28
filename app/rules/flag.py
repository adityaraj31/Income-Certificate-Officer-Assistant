from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class Flag:
    code: str
    severity: str  # "low", "medium", "high", "critical"
    message_hi: str
    evidence: Optional[dict] = None
