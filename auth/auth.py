import os
from typing import Dict, Union

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
import deta
import requests

load_dotenv()

auth_api = FastAPI()
deta = deta.Deta(os.environ.get("DETA_KEY"))
users_db = deta.Base("cotidie-users")

OAUTH2_CLIENT_ID = os.environ.get("OAUTH2_CLIENT_ID")
OAUTH2_CLIENT_SECRET = os.environ.get("OAUTH2_CLIENT_SECRET")
OAUTH2_REDIRECT_URI = os.environ.get("OAUTH2_REDIRECT_URI")

@auth_api.get("/login/discord")
def login() -> RedirectResponse:
    return RedirectResponse(f"https://discord.com/api/v8/oauth2/authorize?client_id={OAUTH2_CLIENT_ID}&scope=identify%20email&response_type=code&redirect_uri={OAUTH2_REDIRECT_URI}")

@auth_api.get("/redirect")
def redirect(code: Union[str, None] = None):
    if code is None:
        return {"error":True, "msg":"code not returned"}

    try:
        token = requests.post(f"https://discord.com/api/v8/oauth2/token", headers={"Content-Type":f"application/x-www-form-urlencoded"}, data={"client_id":OAUTH2_CLIENT_ID, "client_secret":OAUTH2_CLIENT_SECRET, "grant_type":"authorization_code", "code":code, "redirect_uri":OAUTH2_REDIRECT_URI}).json()["access_token"]
        user = requests.get("https://discord.com/api/v8/oauth2/@me", headers={"Authorization":"Bearer "+token}).json()["user"]
        if users_db.get(user["id"]) is not None:
            return {"success":True, "token":token, "new":False, "user":user}
        
        users_db.insert({"username":user["username"], "discriminator":user["discriminator"], "avatar":user["avatar"], "interests":[]}, user["id"])
        return RedirectResponse(os.getenv("FRONTEND_URL", "http://localhost:5000/"), headers={"Token":token})
    except Exception as e:
        return {"error":True, "msg":str(e)}

@auth_api.get("/user")
def get_user(request: Request):
    if request.headers.get("Discord-Token") is None:
        return {"error":True, "msg":"not authenticated"}

    else:
        return requests.get("https://discord.com/api/v8/oauth2/@me", headers={"Authorization":"Bearer "+request.headers.get("Discord-Token", "")}).json()["user"]

@auth_api.get("/user/{user_id}")
def get_user_by_id(user_id: str):
    if users_db.get(str(user_id)) is not None:
        return users_db.get(str(user_id))

    return {"detail":"not found"}
