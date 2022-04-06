from fastapi import FastAPI

from auth.auth import auth_api

api = FastAPI()

api.mount("/auth", auth_api)

@api.get("/")
async def test():
    return {"ok":True}
