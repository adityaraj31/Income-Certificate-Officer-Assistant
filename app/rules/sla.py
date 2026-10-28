from datetime import datetime, timezone
from typing import List, Any
from app.rules.flag import Flag


def check_sla(app: Any, now: datetime = None) -> List[Flag]:
    if now is None:
        now = datetime.now(timezone.utc)
    flags = []
    due = getattr(app, "sla_due_at", None)
    if due is None:
        return flags
    if due.tzinfo is None:
        due_cmp = due.replace(tzinfo=timezone.utc)
    else:
        due_cmp = due.astimezone(timezone.utc)
    if due_cmp < now:
        flags.append(Flag(code="SLA_PAST", severity="critical", message_hi="आवेदन की समय सीमा समाप्त हो चुकी है।", evidence={"sla_due_at": due.isoformat() if hasattr(due, "isoformat") else str(due), "days_past": (now - due_cmp).days}))
    else:
        days_left = (due_cmp - now).days
        if days_left <= 2:
            flags.append(Flag(code="SLA_NEAR", severity="high", message_hi="नियमानुसार समय सीमा निकट है।", evidence={"sla_due_at": due.isoformat() if hasattr(due, "isoformat") else str(due), "days_left": days_left}))
    return flags
