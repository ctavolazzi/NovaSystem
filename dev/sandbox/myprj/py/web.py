import os
from fastapi import FastAPI, APIRouter

app = FastAPI()


@app.on_event("startup")
async def startup():
    # await database.connect()
    print("startup")


@app.on_event("shutdown")
async def shutdown():
    # await database.disconnect()
    print("shutdown")


prefix = APIRouter(prefix=os.getenv("FASTAPI_PREFIX", "/apy"))


@prefix.get("/hello")
async def hello():
    return {"message": "hello!"}

app.include_router(prefix)
