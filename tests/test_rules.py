from datetime import datetime, timedelta, timezone

from app.rules.missing_document import check_missing_document
from app.rules.name_mismatch import check_name_mismatch, normalize_hi_name
from app.rules.expired_address_proof import check_expired_address_proof
from app.rules.low_income import check_low_income_for_occupation
from app.rules.duplicate_applicant import check_duplicate_applicant
from app.rules.sla import check_sla
from app.rules.engine import run_all_checks


class Dummy:
    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)


def test_missing_document_flags():
    docs = [Dummy(doc_type="आय प्रमाण संबंधी अन्य")]  # missing details
    flags = check_missing_document(docs)
    assert any(f.code == "MISSING_DOC" for f in flags)


def test_name_mismatch_basic():
    app = Dummy(applicant_name_hi="रामकुमार", aadhaar_name_hi="राम कुंमार")  # different
    flags = check_name_mismatch(app, [])
    assert any(f.code == "NAME_MISMATCH" for f in flags)


def test_name_mismatch_hindi_variants_mohammad():
    # common variants
    assert normalize_hi_name("मुहम्मद") == normalize_hi_name("मोहम्मद")
    app = Dummy(applicant_name_hi="मुहम्मद अली", aadhaar_name_hi="मोहम्मद अली")
    flags = check_name_mismatch(app, [])
    assert not any(f.code == "NAME_MISMATCH" for f in flags)


def test_name_mismatch_hindi_variants_other():
    assert normalize_hi_name("सीतादेवी") == normalize_hi_name("सीता देवी")
    app = Dummy(applicant_name_hi="सीतादेवी", aadhaar_name_hi="सीता देवी")
    flags = check_name_mismatch(app, [])
    assert not any(f.code == "NAME_MISMATCH" for f in flags)


def test_expired_address_proof():
    now = datetime.now(timezone.utc)
    docs = [Dummy(doc_type="निवास प्रमाण पत्र", expires_on=now - timedelta(days=10))]
    flags = check_expired_address_proof(docs, now=now)
    assert any(f.code == "EXPIRED_ADDRESS_PROOF" for f in flags)


def test_low_income_for_occupation():
    app = Dummy(occupation_hi="छोटा दुकानदार", stated_income_monthly=3000)
    flags = check_low_income_for_occupation(app)
    assert any(f.code == "LOW_INCOME_FOR_OCCUPATION" for f in flags)


def test_duplicate_applicant():
    apps = [Dummy(id=1, applicant_name_hi="राम", father_name_hi="श्याम", address_text_hi="ग्राम A"), Dummy(id=2, applicant_name_hi="राम", father_name_hi="श्याम", address_text_hi="ग्राम A")]
    cur = Dummy(id=2, applicant_name_hi="राम", father_name_hi="श्याम", address_text_hi="ग्राम A")
    flags = check_duplicate_applicant(apps, cur)
    assert any(f.code == "DUPLICATE_APPLICANT" for f in flags)


def test_sla_past_and_near():
    now = datetime.now(timezone.utc)
    app_past = Dummy(sla_due_at=now - timedelta(days=1))
    app_near = Dummy(sla_due_at=now + timedelta(days=1))
    assert any(f.code == "SLA_PAST" for f in check_sla(app_past, now=now))
    assert any(f.code == "SLA_NEAR" for f in check_sla(app_near, now=now))


def test_engine_runs_all():
    now = datetime.now(timezone.utc)
    app = Dummy(id=1, applicant_name_hi="राम", father_name_hi="श्याम", address_text_hi="ग्राम A", occupation_hi="छोटा दुकानदार", stated_income_monthly=3000, aadhaar_name_hi="राम", sla_due_at=now + timedelta(days=1))
    docs = [Dummy(doc_type="आधार कार्ड"), Dummy(doc_type="निवास प्रमाण पत्र", expires_on=now - timedelta(days=5))]
    apps = [app]
    flags = run_all_checks(app, docs, all_apps=apps, now=now)
    codes = {f.code for f in flags}
    assert "EXPIRED_ADDRESS_PROOF" in codes
    assert "LOW_INCOME_FOR_OCCUPATION" in codes
    assert "SLA_NEAR" in codes
