import os
import uuid

from fastapi import FastAPI
from dotenv import load_dotenv
import deta

from auth.auth import auth_api
from models import Event

load_dotenv()

api = FastAPI()
deta = deta.Deta(os.environ.get("DETA_KEY"))
users_db = deta.Base("cotidie-users")
events_db = deta.Base("cotidie-events")

api.mount("/auth", auth_api)

@api.get("/")
async def index():
    return {"ok":True}

@api.post("/new/event")
async def new_event(event: Event):
    pass

@api.get("/event/{event_id}")
async def get_event():
    pass

@api.put("/update/event/{event_id}")
async def update_event(event: Event):
    pass

@api.delete("/delete/event/{event_id}")
async def delete_event(event: Event):
    pass
