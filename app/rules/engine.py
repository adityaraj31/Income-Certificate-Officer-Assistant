from typing import List, Any
from app.rules.flag import Flag
from app.rules.missing_document import check_missing_document
from app.rules.name_mismatch import check_name_mismatch
from app.rules.expired_address_proof import check_expired_address_proof
from app.rules.low_income import check_low_income_for_occupation
from app.rules.duplicate_applicant import check_duplicate_applicant
from app.rules.sla import check_sla


def run_all_checks(app: Any, docs: List[Any], all_apps: List[Any] = None, now=None) -> List[Flag]:
    flags: List[Flag] = []
    flags.extend(check_missing_document(docs))
    flags.extend(check_name_mismatch(app, docs))
    flags.extend(check_expired_address_proof(docs, now=now))
    flags.extend(check_low_income_for_occupation(app))
    if all_apps is not None:
        flags.extend(check_duplicate_applicant(all_apps, app))
    flags.extend(check_sla(app, now=now))
    # deduplicate by code while preserving order
    seen = set()
    res = []
    for f in flags:
        if f.code in seen:
            continue
        seen.add(f.code)
        res.append(f)
    return res
