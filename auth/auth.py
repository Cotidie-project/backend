import os
from typing import Union

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
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5000/")


@auth_api.get("/login/discord")
def login() -> RedirectResponse:
    return RedirectResponse(f"https://discord.com/api/v8/oauth2/authorize?client_id={OAUTH2_CLIENT_ID}&scope=identify%20email&response_type=code&redirect_uri={OAUTH2_REDIRECT_URI}")


@auth_api.get("/redirect")
def redirect(code: Union[str, None] = None):
    if code is None:
        return {"error": True, "msg": "code not returned"}

    try:
        token = requests.post(f"https://discord.com/api/v8/oauth2/token", headers={"Content-Type": f"application/x-www-form-urlencoded"}, data={
                              "client_id": OAUTH2_CLIENT_ID, "client_secret": OAUTH2_CLIENT_SECRET, "grant_type": "authorization_code", "code": code, "redirect_uri": OAUTH2_REDIRECT_URI}).json()["access_token"]
        user = requests.get("https://discord.com/api/v8/oauth2/@me",
                            headers={"Authorization": "Bearer "+token}).json()["user"]
        if users_db.get(user["id"]) is not None:
            rr = RedirectResponse(FRONTEND_URL)
            rr.set_cookie("token", token)
            return rr

        users_db.insert({"username": user["username"], "discriminator": user["discriminator"],
                        "avatar": user["avatar"], "points": 0}, user["id"])
        rr = RedirectResponse(FRONTEND_URL)
        rr.set_cookie("token", token)
        return rr
    except Exception as e:
        return {"error": True, "msg": str(e)}


@auth_api.get("/user")
def get_user(request: Request):
    if request.headers.get("Discord-Token") is None:
        return {"error": True, "msg": "not authenticated"}

    else:
        return requests.get("https://discord.com/api/oauth2/@me", headers={"Authorization": "Bearer "+request.headers.get("Discord-Token", "")}).json()["user"]


@auth_api.get("/user/{user_id}")
def get_user_by_id(user_id: str):
    if users_db.get(str(user_id)) is not None:
        return users_db.get(str(user_id))

    return {"detail": "not found"}

@auth_api.put("/user/update/{user_id}/{points}")
def update_user_points(user_id: str, points: int, token: str):
    user = users_db.get(user_id)
    if user is None:
        return {"error":True, "msg":"user does not exist"}

    if not isinstance(points, int):
        return {"error":True, "msg":"points must be a number"}

    try:
        if requests.get("https://discord.com/api/oauth2/@me", headers={"Authorization":"Bearer "+token}).json()["user"]["id"] == user_id:
            users_db.put({"username":user["username"], "discriminator":user["discriminator"], "avatar":user["avatar"], "points":points}, user_id)
            return {"success":True}

        return {"error":True, "msg":"token and id do not match"}
    except Exception:
        return {"error":True, "msg":"invalid token"}
