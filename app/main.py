from fastapi import FastAPI
from app.routes import router

app = FastAPI(title="My Microservice")

app.include_router(router)
