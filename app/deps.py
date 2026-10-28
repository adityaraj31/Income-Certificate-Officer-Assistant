from fastapi import Request, HTTPException
from itsdangerous import URLSafeTimedSerializer
from sqlmodel import Session, select

from app.db import engine
from app import models

SECRET_KEY = "dev-secret-key-change-in-prod"
serializer = URLSafeTimedSerializer(SECRET_KEY)


def create_session_token(officer_id: int) -> str:
    return serializer.dumps({"officer_id": officer_id})


def get_current_officer(request: Request):
    token = request.cookies.get("session")
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        data = serializer.loads(token, max_age=60 * 60 * 8)
        officer_id = data.get("officer_id")
    except Exception:
        raise HTTPException(status_code=401, detail="Unauthorized")
    with Session(engine) as session:
        officer = session.get(models.Officer, officer_id)
        if not officer:
            raise HTTPException(status_code=401, detail="Unauthorized")
        return officer
