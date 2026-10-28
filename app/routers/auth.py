from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from app.db import engine
from app import models
from app.auth import verify_password

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/login", response_class=HTMLResponse)
def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
def login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    with Session(engine) as session:
        officer = session.exec(select(models.Officer).where(models.Officer.username == username)).first()
        if not officer or not verify_password(password, officer.password_hash):
            return templates.TemplateResponse("login.html", {"request": request, "error": "गलत यूज़रनेम या पासवर्ड"})
        from app.deps import create_session_token
        token = create_session_token(officer.id)
        resp = RedirectResponse(url="/dashboard", status_code=302)
        resp.set_cookie(key="session", value=token, httponly=True, max_age=8*3600)
        return resp


@router.get("/logout")
def logout():
    resp = RedirectResponse(url="/login", status_code=302)
    resp.delete_cookie("session")
    return resp
