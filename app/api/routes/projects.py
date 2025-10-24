from fastapi import APIRouter, HTTPException, Header
from app.models.pydantic_models import ProjectCreate, ProjectOut
from app.db.mongo import get_projects_collection
from app.core import scheduler

router = APIRouter(prefix="/projects")


@router.post("/", response_model=ProjectOut)
async def create_project(p: ProjectCreate, x_user_id: str | None = Header(None)):
    if not x_user_id:
        raise HTTPException(401, "Missing X-User-Id header (use real auth in prod)")
    coll = get_projects_collection()
    doc = p.dict()
    doc.update(
        {"owner_id": x_user_id, "status": "running"}
    )
    res = await coll.insert_one(doc)
    doc["_id"] = res.inserted_id
    scheduler.start_project(doc)
    return {
        "id": str(doc["_id"]),
        "name": doc["name"],
        "type": doc["type"],
        "url": doc.get("url"),
        "interval_s": doc.get("interval_s"),
        "status": doc.get("status")
    }


@router.get("/")
async def list_projects(x_user_id: str | None = Header(None)):
    if not x_user_id:
        raise HTTPException(401, "Missing X-User-Id header")
    coll = get_projects_collection()
    out = []
    async for p in coll.find({"owner_id": x_user_id}):
        out.append({
            "id": str(p["_id"]),
            "name": p["name"],
            "type": p["type"],
            "url": p.get("url"),
            "interval_s": p.get("interval_s"),
            "status": p.get("status")
        })
    return out
