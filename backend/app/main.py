from app.api.routes import auth, health, score, users
from fastapi import FastAPI

app = FastAPI(
    title="DevStats",
    description="DevStats is a tool to track developer statistics",
    version="0.0.1",
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(score.router)
