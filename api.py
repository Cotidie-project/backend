import os
import uuid

from fastapi import FastAPI
from dotenv import load_dotenv
import deta

from auth.auth import auth_api
from models import Interest

load_dotenv()

api = FastAPI()
deta = deta.Deta(os.environ.get("DETA_KEY"))
users_db = deta.Base("cotidie-users")
interests_db = deta.Base("cotidie-interests")

api.mount("/auth", auth_api)

@api.get("/")
async def test():
    return {"ok":True}

@api.get("/new/interest")
def new_interest(interest: Interest):
    interest_id = str(uuid.uuid4())
    interests_db.insert({"name":interest.name, "source":interest.source, "source_type":interest.source_type}, interest_id)
    return {"id":interest_id}

@api.get("/interests")
def get_interests():
    res = interests_db.fetch()
    interests = res.items

    while res.last:
        res = interests_db.fetch(last=res.last)
        interests += res.items

    return interests

@api.get("/interests/{user_id}")
def get_user_interests(user_id: str):
    return users_db.get(user_id)["interests"]

@api.put("/update/interests/{user_id}")
def update_user_interests(user_id: str, interest: Interest):
    user = users_db.get(user_id)    

    if user is None:
        return {"error":True, "msg":"user doesnt exist"}

    upd_user = user
    upd_user["interests"].append({"name":interest.name, "source":interest.source, "source_type":interest.source_type})
    users_db.put(upd_user)
    return {"success":True, "msg":"user interests updated successfully", "user":upd_user}
