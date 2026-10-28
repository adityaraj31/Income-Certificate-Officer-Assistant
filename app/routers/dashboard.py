from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from datetime import datetime, timezone

from app.db import engine
from app import models
from app.deps import get_current_officer
from app.rules.engine import run_all_checks
from app.rules.priority import score_application, priority_level

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, officer = Depends(get_current_officer), filter: str = None):
    with Session(engine) as session:
        apps = session.exec(select(models.Application)).all()
        now = datetime.now(timezone.utc)
        items = []
        for app in apps:
            docs = session.exec(select(models.Document).where(models.Document.application_id == app.id)).all()
            flags = run_all_checks(app, docs, apps, now=now)
            days_left = 0
            if app.sla_due_at:
                due = app.sla_due_at
                if due.tzinfo is None:
                    due_cmp = due.replace(tzinfo=timezone.utc)
                else:
                    due_cmp = due.astimezone(timezone.utc)
                days_left = (due_cmp - now).days
            sc = score_application(flags, days_left)
            pr = priority_level(sc)
            reason = ""
            if days_left < 0:
                reason = f"अंतिम तिथि {abs(days_left)} दिन पूर्व समाप्त"
            elif days_left <= 2:
                reason = f"अंतिम तिथि {days_left} दिन शेष"
            elif flags:
                reason = flags[0].message_hi
            items.append({"app": app, "flags": flags, "days_left": days_left, "score": sc, "priority": pr, "reason": reason})
        # apply filters
        if filter == "today":
            items = [i for i in items if i["days_left"] <= 0]  # today/final
        elif filter == "warning":
            items = [i for i in items if i["days_left"] <= 2 or any(f.severity in ["high", "critical"] for f in i["flags"])]
        elif filter == "returned":
            items = [i for i in items if i["app"].status == "वापस"]
        items_sorted = sorted(items, key=lambda x: x["score"], reverse=True)
        total_pending = len([i for i in items if i["app"].status == "पेंडिंग"])
        today_final = len([i for i in items if i["days_left"] <= 0])
        warning = len([i for i in items if i["days_left"] <= 2 or any(f.severity in ["high", "critical"] for f in i["flags"])])
        returned = len([i for i in items if i["app"].status == "वापस"])
        return templates.TemplateResponse("dashboard.html", {"request": request, "officer": officer, "items": items_sorted, "total_pending": total_pending, "today_final": today_final, "warning": warning, "returned": returned, "filter": filter})
