import uvicorn

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi import Request
from contextlib import asynccontextmanager

from starlette.staticfiles import StaticFiles

from app.api.routes import auth, projects, teleram, users
from app.db.mongo import get_mongo_client, close_mongo_client
from app.db.pg import connect_to_pg, close_pg
from app.core.scheduler import restore_running_projects


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_pg()
    get_mongo_client()
    try:
        await restore_running_projects()
    except Exception:
        pass

    yield
    close_mongo_client()
    await close_pg()


app = FastAPI(title="Pinger", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router, prefix="/api/auth")
app.include_router(projects.router, prefix="/api/projects")
app.include_router(teleram.router, prefix="/api/telegram")
app.include_router(users.router, prefix="/api/users")


@app.get("/", response_class=HTMLResponse, summary="Just frontend", description="Not description")
async def serve_frontend(request: Request):
    with open("static/index.html") as f:
        return HTMLResponse(content=f.read())

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5123, reload=True)
