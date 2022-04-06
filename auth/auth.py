import os
from typing import Dict, Union

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
import requests

load_dotenv()

auth_api = FastAPI()

OAUTH2_CLIENT_ID = os.environ.get("OAUTH2_CLIENT_ID")
OAUTH2_CLIENT_SECRET = os.environ.get("OAUTH2_CLIENT_SECRET")
OAUTH2_REDIRECT_URI = os.environ.get("OAUTH2_REDIRECT_URI")

@auth_api.get("/login")
def login() -> RedirectResponse:
    return RedirectResponse(f"https://discordapp.com/api/oauth2/authorize?client_id={OAUTH2_CLIENT_ID}&scope=identify%20email&response_type=code&redirect_uri={OAUTH2_REDIRECT_URI}")

@auth_api.get("/redirect")
def redirect(code: Union[str, None] = None) -> Dict[str, Union[str, bool]]:
    if code is None:
        return {"error":True, "msg":"code not returned"}

    token = requests.post(f"https://discord.com/api/v8/oauth2/token", headers={"Content-Type":f"application/x-www-form-urlencoded"}, data={"client_id":OAUTH2_CLIENT_ID, "client_secret":OAUTH2_CLIENT_SECRET, "grant_type":"authorization_code", "code":code, "redirect_uri":OAUTH2_REDIRECT_URI}).json()["access_token"]
    return {"success":True, "token":token}
