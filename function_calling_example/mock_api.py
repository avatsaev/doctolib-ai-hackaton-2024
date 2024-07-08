from typing import List
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import time

app = FastAPI()


class Appointment(BaseModel):
    id: int
    date_time: str
    doctor_name: str


appointments = [
    {
        "id": 1,
        "date_time": "2022-12-01T14:30:00",
        "doctor_name": "Ricardo Delinion"
    },
    {
        "id": 2,
        "date_time": "2024-08-01T15:45:00",
        "doctor_name": "Linora Komilio"
    },
]


def get_past_appointments():
    now = datetime.now()
    return [appointment for appointment in appointments if parse_datetime(appointment['date_time']) < now]


def get_future_appointments():
    now = datetime.now()
    return [appointment for appointment in appointments if parse_datetime(appointment['date_time']) > now]


def parse_datetime(datetime_str):
    # Adjusting the timezone (add 3 hours here)
    return datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S") + timedelta(hours=3)


@app.get("/appointments", response_model=List[Appointment])
async def get_all():
    return appointments


@app.get("/appointments/past", response_model=List[Appointment])
async def get_past():
    past = get_past_appointments()
    if not past:
        raise HTTPException(
            status_code=404, detail="No past appointments found.")
    return past


@app.get("/appointments/future", response_model=List[Appointment])
async def get_future():
    future = get_future_appointments()
    if not future:
        raise HTTPException(
            status_code=404, detail="No future appointments found.")
    return future
