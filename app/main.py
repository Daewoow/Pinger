import uvicorn

from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api.routes import auth, projects, teleram
from app.db.mongo import get_mongo_client
from app.core.scheduler import restore_running_projects


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_mongo_client()
    try:
        await restore_running_projects()
    except Exception:
        pass

    yield
    pass


app = FastAPI(title="Pinger", lifespan=lifespan)

app.include_router(auth.router, prefix="/api/auth")
app.include_router(projects.router, prefix="/api/projects")
app.include_router(teleram.router, prefix="/api/telegram")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5123)
