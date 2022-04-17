import os
import uuid

from fastapi import FastAPI
from dotenv import load_dotenv
import deta
import requests

from auth.auth import auth_api
from plan import plan_api
from models import Task, UpdateTask, Break

load_dotenv()

api = FastAPI()
deta = deta.Deta(os.environ.get("DETA_KEY"))
users_db = deta.Base("cotidie-users")
tasks_db = deta.Base("cotidie-tasks")
breaks_db = deta.Base("cotidie-breaks")

api.mount("/api/auth", auth_api)
api.mount("/api/plan", plan_api)

@api.get("/api")
async def index():
    return {"ok":True}

@api.post("/api/new/task")
async def new_task(task: Task, token: str):
    if token is None or token == "":
        return {"error":"no token present"}
    user_id = requests.get("https://discord.com/api/oauth2/@me", headers={"Authorization":"Bearer "+token}).json()["user"]["id"]
    tid = str(uuid.uuid4())
    tasks_db.insert({"name":task.name, "description":task.description, "date":task.date, "time":task.time, "duration":task.duration, "completed":task.completed, "points":task.points, "id":user_id}, tid)
    return {"success":True}

@api.get("/api/task/{task_id}")
async def get_task(task_id: str):
    task = tasks_db.get(task_id)
    if task is None:
        return {"error":"task does not exist"}
    return task

@api.get("/api/tasks/@me")
async def get_tasks(token: str):
    return tasks_db.fetch({"id":requests.get("https://discord.com/api/oauth2/@me", headers={"Authorization":"Bearer "+token}).json()["user"]["id"]}).items

@api.put("/api/update/task/{task_id}")
async def update_task(task: UpdateTask, task_id: str, token: str):
    user_id = requests.get("https://discord.com/api/oauth2/@me", headers={"Authorization":"Bearer "+token}).json()["user"]["id"]
    if (task_:=tasks_db.get(task_id)) is not None:
        tasks_db.put({"name":task.name, "description":task.description, "points":task.points, "completed":task.completed, "date":task_["date"], "time":task_["time"], "duration":task_["duration"], "id":user_id}, task_id)
        return {"success":True}
    return {"error":"task does not exist"}

@api.delete("/api/delete/task/{task_id}")
async def delete_task(task_id: str):
    task = tasks_db.get(task_id)
    if task is None:
        return {"error":"task does not exist"}
    tasks_db.delete(task_id)
    return {"success":True}

@api.post("/api/new/break")
async def new_break(break_: Break, token: str):
    if token is None or token == "":
        return {"error":"no token present"}
    user_id = requests.get("https://discord.com/api/oauth2/@me", headers={"Authorization":"Bearer "+token}).json()["user"]["id"]
    bid = str(uuid.uuid4())
    breaks_db.insert({"name":break_.name, "stime":break_.stime, "btime":break_.etime, "id":user_id}, bid)
    return {"success":True}    

@api.get("/api/break/{break_id}")
async def get_break(break_id: str):
    break_ = breaks_db.get(break_id)
    if break_ is None:
        return {"error":"break does not exist"}
    return break_

@api.get("/api/breaks/@me")
def get_breaks(token: str):
    return breaks_db.fetch({"id":requests.get("https://discord.com/api/oauth2/@me", headers={"Authorization":"Bearer "+token}).json()["user"]["id"]}).items

@api.put("/api/update/break/{break_id}")
async def update_break(break_: Break, break_id: str, token: str):
    user_id = requests.get("https://discord.com/api/oauth2/@me", headers={"Authorization":"Bearer "+token}).json()["user"]["id"]
    if breaks_db.get(break_id) is not None:
        breaks_db.put({"name":break_.name, "stime":break_.stime, "etime":break_.etime, "id":user_id}, break_id)
        return {"success":True}
    return {"error":"task does not exist"}

@api.delete("/api/delete/break/{break_id}")
async def delete_break(break_id: str):
    break_ = breaks_db.get(break_id)
    if break_ is None:
        return {"error":"task does not exist"}
    breaks_db.delete(break_id)
    return {"success":True}
