import logging
import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth, projects
from app.db.mongo import get_mongo_client
from app.core.scheduler import restore_running_projects

app = FastAPI()

app.include_router(auth.router, prefix="/api")
app.include_router(projects.router, prefix="/api")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("alerter:main")


@app.on_event("startup")
async def startup():
    get_mongo_client()
    await restore_running_projects()


@app.on_event("shutdown")
async def shutdown():
    pass

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=5123, reload=True)

