from typing import List, Any
from app.rules.flag import Flag


def check_low_income_for_occupation(app: Any) -> List[Flag]:
    flags = []
    occ = getattr(app, "occupation_hi", "") or ""
    inc = getattr(app, "stated_income_monthly", 0) or 0
    try:
        inc_int = int(inc)
    except Exception:
        inc_int = 0
    # simple heuristic per rules
    if "दुकानदार" in occ and inc_int < 5000:
        flags.append(Flag(code="LOW_INCOME_FOR_OCCUPATION", severity="medium", message_hi="व्यवसाय के अनुरूप आय न्यून प्रतीत होती है।", evidence={"occupation_hi": occ, "stated_income_monthly": inc_int}))
    elif any(x in occ for x in ["राजमिस्त्री", "कारीगर"]) and inc_int < 6000:
        flags.append(Flag(code="LOW_INCOME_FOR_OCCUPATION", severity="medium", message_hi="व्यवसाय के अनुरूप आय न्यून प्रतीत होती है।", evidence={"occupation_hi": occ, "stated_income_monthly": inc_int}))
    elif any(x in occ for x in ["कृषि मजदूर", "दिहाड़ी मजदूर", "रिक्शा चालक"]) and inc_int < 3000:
        flags.append(Flag(code="LOW_INCOME_FOR_OCCUPATION", severity="medium", message_hi="व्यवसाय के अनुरूप आय न्यून प्रतीत होती है।", evidence={"occupation_hi": occ, "stated_income_monthly": inc_int}))
    elif inc_int < 2000:  # very low
        flags.append(Flag(code="LOW_INCOME_FOR_OCCUPATION", severity="medium", message_hi="व्यवसाय के अनुरूप आय न्यून प्रतीत होती है।", evidence={"occupation_hi": occ, "stated_income_monthly": inc_int}))
    return flags
