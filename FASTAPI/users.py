from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

@app.get("/users")
async def GetUsers():
    return [{"name":"Katie"}]