from fastapi import FastAPI

 

app = FastAPI()

@app.get("/url")
async def root():
    return {"message": "Hola desde FastAPI "}