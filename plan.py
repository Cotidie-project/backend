import os
from typing import Union

from models import Plan

from fastapi import FastAPI
from dotenv import load_dotenv
import requests
import deta

load_dotenv()

plan_api = FastAPI()
deta = deta.Deta(os.environ.get("DETA_KEY"))
users_db = deta.Base("cotidie-users")

def int_to_time_str(hr: float):
    hr_str = str(hr)
    if isinstance(hr, float):
        hr_list = hr_str.split(".")
        hr_int = int(hr_list[0])
        min_int = int(hr_list[1]*60)
        return f"{hr_int}:{min_int}"
    return f"{hr}:00"

def find_available_time(schedule, time_int, tpt):
    time_str = int_to_time_str(time_int)
    if time_str in schedule.keys():
        return find_available_time(schedule, time_int+tpt, tpt)
    else:
        return time_int

@plan_api.post("/")
def plan_(plan: Plan, plan_type: str, token: str):
    if plan_type.lower() not in ["day", "week"]:
        return {"error":"invalid plan type"}

    if plan.tasks == []:
        return {"error":"can not plan for no tasks"}

    user = users_db.get(requests.get("https://discord.com/api/oauth2/@me", headers={"Authorization":"Bearer "+token}).json()["user"]["id"])
    if user is None:
        return {"error":"user does not exist"}

    schedule = {}
    for break_ in plan.breaks:
        schedule[break_["stime"]] = {"type":"break", "name":break_["name"]}
    
    day_start = 8
    day_end = 22
    day_duration = day_end-day_start
    time_per_task = (day_duration-len(plan.breaks))/len(plan.tasks)
    
    for task in plan.tasks:
        time = day_start
        if find_available_time(schedule, time, time_per_task) > day_end-time_per_task:
            return {"error":"schedule is filled"}
        schedule[int_to_time_str(find_available_time(schedule, time, time_per_task))] = {"type":"task", "name":task["name"], "desc":task["description"]}

    return schedule
