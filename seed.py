#!/usr/bin/env python3
import json
from datetime import datetime, timedelta, timezone
from sqlmodel import Session, select

from app.db import engine, create_db_and_tables
from app import models


from app.auth import hash_password

OFFICERS = [
    {"name": "राजेश कुमार", "designation": "लेखपाल", "username": "rajesh_kumar", "password": "rajesh123"},
    {"name": "आशा देवी", "designation": "तहसीलदार सहायक", "username": "asha_devi", "password": "asha123"},
]

FIRST_NAMES = ["रामकुमार", "सीता", "मोहन", "गायत्री", "अजय", "पूजा", "विनोद", "सुनिता", "राकेश", "कविता", "शिवकुमार", "नीतू", "मनीष", "अनिता", "सुरेश", "रीमा", "ओमप्रकाश", "शारदा", "दिलीप", "सरोज", "भानु", "मीरा", "हरिओम", "लता", "योगेश"]
FATHERS = ["श्री रामलाल", "श्री मंगीलाल", "श्री जगदीश", "श्री प्रेमचंद", "श्री हरिशंकर", "श्री कैलाश", "श्री बाबूलाल", "श्री सत्यनारायण", "श्री किशोरीलाल", "श्री राधेश्याम"]
VILLAGES = ["महमूदपुर", "सिकंदरपुर", "खेतापुर", "गंगापुर", "रामनगर", "देवपुर", "भदौरा", "नरायनपुर", "जैतपुर", "बाँदा रोड"]
TEHSILS = ["सदर", "करछना", "हंडिया", "मेजा", "बारा"]
DISTRICTS = ["प्रयागराज"]

OCCUPATIONS = ["कृषि मजदूर", "दिहाड़ी मजदूर", "नाई", "मोची", "रिक्शा चालक", "घरेलू काम", "छोटा दुकानदार", "मजदूर", "राजमिस्त्री"]
AADHAAR_NAMES_DIFF = ["रामकुंवर", "सीतादेवी", "मोहनलाल सिंह", "गायत्री बाई"]


def seed_all(session: Session):
    # Officers
    for o in OFFICERS:
        session.add(models.Officer(name=o["name"], designation=o["designation"], username=o["username"], password_hash=hash_password(o.get("password", "pass123"))))
    session.commit()

    officers = session.exec(select(models.Officer)).all()
    officer_ids = [o.id for o in officers]

    base_now = datetime.now(timezone.utc)
    apps_to_create = []

    # Create 25 applications covering cases
    for i in range(25):
        idx = i
        applicant = FIRST_NAMES[idx % len(FIRST_NAMES)]
        father = FATHERS[idx % len(FATHERS)]
        aadhaar_last4 = f"{1000 + idx:04d}"
        aadhaar_name = applicant
        # Case: Aadhaar vs application name mismatch
        if idx in [1, 6, 11, 16, 21]:
            aadhaar_name = AADHAAR_NAMES_DIFF[idx % len(AADHAAR_NAMES_DIFF)]
        village = VILLAGES[idx % len(VILLAGES)]
        tehsil = TEHSILS[idx % len(TEHSILS)]
        district = DISTRICTS[0]
        address_text_hi = f"ग्राम {village}, तहसील {tehsil}, जनपद {district}"
        occupation = OCCUPATIONS[idx % len(OCCUPATIONS)]
        # Case: income too low for stated occupation
        if idx in [2, 7, 12, 17, 22]:
            stated_income_monthly = 1500 + (idx * 50)
        elif occupation in ["छोटा दुकानदार", "राजमिस्त्री"]:
            stated_income_monthly = 9000 + (idx * 150)
        else:
            stated_income_monthly = 4000 + (idx * 100)
        family_members = 3 + (idx % 4)
        # SLA cases
        if idx in [3, 8, 13, 18, 23]:  # near SLA (due in 1-2 days)
            submitted_at = base_now - timedelta(days=25)
            sla_due_at = base_now + timedelta(days=1)
        elif idx in [4, 9, 14, 19, 24]:  # past SLA
            submitted_at = base_now - timedelta(days=40)
            sla_due_at = base_now - timedelta(days=5)
        else:
            submitted_at = base_now - timedelta(days=10 - (idx % 5))
            sla_due_at = base_now + timedelta(days=15 - (idx % 7))
        flags = []
        # Assign flags by cases
        if idx in [1, 6, 11, 16, 21]:
            flags.append("आधार एवं आवेदन में नाम का अंतर")
        if idx in [5, 10, 15, 20]:
            flags.append("आवश्यक दस्तावेज़ अनुपलब्ध")
        if idx in [0, 5, 10, 15, 20]:  # some clean or missing docs
            pass
        if idx in [2, 7, 12, 17, 22]:
            flags.append("व्यवसाय के अनुरूप आय न्यून प्रतीत")
        if idx in [3, 8, 13, 18, 23]:
            flags.append("नियमानुसार समय सीमा निकट")
        if idx in [4, 9, 14, 19, 24]:
            flags.append("नियमानुसार समय सीमा समाप्त")
        # duplicate applicant case
        if idx == 0:
            applicant = FIRST_NAMES[1]
            father = FATHERS[1]
            flags.append("समान आवेदक का पूर्व आवेदन संभव")

        app = models.Application(
            applicant_name_hi=applicant,
            father_name_hi=father,
            aadhaar_last4=aadhaar_last4,
            address_text_hi=address_text_hi,
            occupation_hi=occupation,
            stated_income_monthly=stated_income_monthly,
            family_members=family_members,
            village=village,
            tehsil=tehsil,
            district=district,
            submitted_at=submitted_at,
            sla_due_at=sla_due_at,
            status="पेंडिंग",
            flags_json=json.dumps(flags, ensure_ascii=False),
            aadhaar_name_hi=aadhaar_name,
        )
        session.add(app)
        apps_to_create.append((app, idx))
    session.commit()

    # Reload apps
    apps = session.exec(select(models.Application)).all()
    # Add documents
    for app in apps:
        idx = apps.index(app)
        # expired address proof
        if idx in [25 % 25]:  # will handle by specific
            pass
    # Set specific document cases
    for i, app in enumerate(apps):
        # expired address proof
        if i % 5 == 0 and i != 0:
            session.add(models.Document(
                application_id=app.id,
                doc_type="निवास प्रमाण पत्र",
                issued_on=base_now - timedelta(days=800),
                expires_on=base_now - timedelta(days=30),
                number_masked="XX-1234",
            ))
            if "निवास प्रमाण पत्र की वैधता समाप्त" not in json.loads(app.flags_json):
                flags = json.loads(app.flags_json)
                flags.append("निवास प्रमाण पत्र की वैधता समाप्त")
                app.flags_json = json.dumps(flags, ensure_ascii=False)
        # missing document
        if i in [5, 10, 15, 20]:
            session.add(models.Document(
                application_id=app.id,
                doc_type="आय प्रमाण संबंधी अन्य",
                issued_on=None,
                expires_on=None,
                number_masked=None,
            ))
            flags = json.loads(app.flags_json)
            if "आवश्यक दस्तावेज़ अनुपलब्ध" not in flags:
                flags.append("आवश्यक दस्तावेज़ अनुपलब्ध")
            app.flags_json = json.dumps(flags, ensure_ascii=False)
        else:
            session.add(models.Document(
                application_id=app.id,
                doc_type="आधार कार्ड",
                issued_on=base_now - timedelta(days=365),
                expires_on=None,
                number_masked=f"XXXX-XXXX-{app.aadhaar_last4}",
            ))
            session.add(models.Document(
                application_id=app.id,
                doc_type="निवास प्रमाण पत्र",
                issued_on=base_now - timedelta(days=60),
                expires_on=base_now + timedelta(days=365),
                number_masked="XX-5678",
            ))
    session.commit()
    print(f"Seeded {len(officers)} officers and {len(apps)} applications")


def seed():
    create_db_and_tables()
    with Session(engine) as session:
        officers = session.exec(select(models.Officer)).all()
        apps = session.exec(select(models.Application)).all()
        if officers and apps:
            print("डेटाबेस में पहले से डेटा मौजूद है।")
            return
        seed_all(session)


if __name__ == "__main__":
    seed()
