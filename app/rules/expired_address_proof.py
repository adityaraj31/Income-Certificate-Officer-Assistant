from datetime import datetime, timezone
from typing import List, Any
from app.rules.flag import Flag


def check_expired_address_proof(docs: List[Any], now: datetime = None) -> List[Flag]:
    if now is None:
        now = datetime.now(timezone.utc)
    flags = []
    for d in docs:
        dt = getattr(d, "doc_type", "") or ""
        if "निवास" in dt or "पता" in dt:
            exp = getattr(d, "expires_on", None)
            if exp is not None:
                # handle naive/aware
                if exp.tzinfo is None:
                    exp_cmp = exp.replace(tzinfo=timezone.utc)
                else:
                    exp_cmp = exp.astimezone(timezone.utc)
                if exp_cmp < now:
                    flags.append(Flag(code="EXPIRED_ADDRESS_PROOF", severity="high", message_hi="निवास प्रमाण पत्र की वैधता समाप्त हो चुकी है।", evidence={"doc_id": getattr(d, "id", None), "expires_on": exp.isoformat() if hasattr(exp, "isoformat") else str(exp)}))
                    break
    return flags
