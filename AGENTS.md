# Project: आय प्रमाण पत्र – अधिकारी सहायक (Income Certificate Officer Assistant)

A Hindi-language tool for UP Tehsil officers to review income certificate applications.
All data is fictional. Never use real citizen data.

## Rules
- All user-facing text is Hindi (Devanagari) with proper administrative terms. Strings live in app/i18n/hi.py, never hardcoded in templates or routes.
- AI only SUGGESTS. Approve / Reject / Return are explicit officer actions. Reject and Return require a remark (server-side validation, not just UI).
- Flags come from deterministic code in app/rules/. The LLM only writes the summary and reasoning from those flags and may not add new flags. If the LLM fails or has no key, use app/ai/fallback.py.
- LLM output is parsed into a Pydantic model; on invalid output, fall back.
- Every decision writes an audit_log row: AI suggestion, officer decision, agreed (bool), remark, officer id, timestamp.
- Type hints everywhere. Small pure functions. pytest for every rule.
- Server-rendered Jinja2 + HTMX. Mobile-friendly, accessible (contrast, labels, large tap targets).

## Stack
FastAPI, Jinja2, HTMX, Tailwind, SQLModel/SQLite, pytest, uvicorn.

## Commands
uvicorn app.main:app --reload | pytest | python seed.py