from typing import List, Any
from app.rules.flag import Flag


def check_duplicate_applicant(apps: List[Any], current_app: Any) -> List[Flag]:
    flags = []
    cur_name = (getattr(current_app, "applicant_name_hi", "") or "").strip()
    cur_father = (getattr(current_app, "father_name_hi", "") or "").strip()
    cur_addr = (getattr(current_app, "address_text_hi", "") or "").strip()
    for a in apps:
        if getattr(a, "id", None) == getattr(current_app, "id", None):
            continue
        if (getattr(a, "applicant_name_hi", "") or "").strip() == cur_name and (getattr(a, "father_name_hi", "") or "").strip() == cur_father and (getattr(a, "address_text_hi", "") or "").strip() == cur_addr:
            flags.append(Flag(code="DUPLICATE_APPLICANT", severity="critical", message_hi="समान आवेदक का पूर्व आवेदन संभव है।", evidence={"duplicate_app_id": getattr(a, "id")}))
            break
    return flags
