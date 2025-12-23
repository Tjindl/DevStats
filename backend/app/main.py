from fastapi import FastAPI

from app.api.routes import auth, users, score

app = FastAPI(
    title="DevStats",
    description="DevStats is a tool to track developer statistics",
    version="0.0.1",
)


# Health Check
@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(score.router)


