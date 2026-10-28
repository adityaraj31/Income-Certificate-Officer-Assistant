from datetime import datetime, timezone
from typing import List, Any
from app.rules.flag import Flag


def check_missing_document(docs: List[Any]) -> List[Flag]:
    flags = []
    # check if any required doc marked missing or has no ref/issued_on in context
    has_aadhaar = False
    has_address = False
    for d in docs:
        dt = getattr(d, "doc_type", "") or ""
        if "आधार" in dt:
            has_aadhaar = True
        if "निवास" in dt or "पता" in dt:
            has_address = True
        # if doc marked as other/missing with no details
        if dt.strip() == "आय प्रमाण संबंधी अन्य" and not getattr(d, "issued_on", None) and not getattr(d, "file_ref", None):
            flags.append(Flag(code="MISSING_DOC", severity="high", message_hi="आवश्यक दस्तावेज़ अनुपलब्ध है।", evidence={"doc_type": dt}))
    if not has_aadhaar:
        flags.append(Flag(code="MISSING_DOC", severity="high", message_hi="आधार कार्ड संबंधी दस्तावेज़ अनुपलब्ध प्रतीत होता है।", evidence={"missing": "aadhaar"}))
    if not has_address:
        flags.append(Flag(code="MISSING_DOC", severity="high", message_hi="निवास प्रमाण पत्र अनुपलब्ध प्रतीत होता है।", evidence={"missing": "address_proof"}))
    return flags
