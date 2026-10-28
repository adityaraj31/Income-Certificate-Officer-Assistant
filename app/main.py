from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.db import create_db_and_tables, engine
from app import models  # ensure tables registered
from sqlmodel import Session, select
from app import seed


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    with Session(engine) as session:
        officers = session.exec(select(models.Officer)).all()
        apps = session.exec(select(models.Application)).all()
        if not officers or not apps:
            seed.seed_all(session)
    yield


app = FastAPI(title="आय प्रमाण पत्र – अधिकारी सहायक", lifespan=lifespan)


@app.get("/")
def root():
    return {"message": "आय प्रमाण पत्र – अधिकारी सहायक (स्वागत)"}
