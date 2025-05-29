import uvicorn
from fastapi import FastAPI, Depends
from starlette.middleware.cors import CORSMiddleware
from api.v1.routers import router as api_routers
from database.init_db import init_db

from exception.base import CustomException
from exception.exception_handler import custom_exception_handler
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_routers)

app.add_exception_handler(CustomException, custom_exception_handler)

@app.on_event("startup")
async def startup_event():
    await init_db()

HOST = "127.0.0.1"
PORT = 8080


if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)