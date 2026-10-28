from typing import List, Any
from app.rules.flag import Flag


def normalize_hi_name(s: str) -> str:
    if not s:
        return ""
    t = s.strip()
    # normalize common variants
    t = t.replace("मुहम्मद", "मोहम्मद")
    t = t.replace("मुहंमद", "मोहम्मद")
    t = t.replace("मोहम्मद", "मोहम्मद")  # canonical
    t = t.replace("कुंवर", "कुँवर")
    t = t.replace("कुँवर", "कुंवर")  # normalize spacing/nuqta variants simply
    # more specific
    t = t.replace("सीतादेवी", "सीता देवी")
    t = t.replace("गायत्रीबाई", "गायत्री बाई")
    # collapse spaces
    import re
    t = re.sub(r"\s+", " ", t)
    return t


def check_name_mismatch(app: Any, docs: List[Any]) -> List[Flag]:
    flags = []
    app_name = getattr(app, "applicant_name_hi", "") or ""
    aadhaar_name = getattr(app, "aadhaar_name_hi", "") or ""
    if not aadhaar_name:
        # try to infer from docs? skip if none
        pass
    n_app = normalize_hi_name(app_name)
    n_aa = normalize_hi_name(aadhaar_name)
    if aadhaar_name and n_app and n_aa and n_app != n_aa:
        flags.append(Flag(code="NAME_MISMATCH", severity="high", message_hi="आधार एवं आवेदन में नाम का अंतर पाया गया है।", evidence={"applicant_name_hi": app_name, "aadhaar_name_hi": aadhaar_name}))
    return flags
