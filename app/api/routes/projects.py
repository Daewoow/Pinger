from fastapi import APIRouter, Depends, HTTPException, Path, Query
from app.models.pydantic_models import ProjectCreate
from app.db.mongo import get_projects_collection, get_errors_collection
from app.core import scheduler
from app.core.auth import get_current_user
from bson import ObjectId


router = APIRouter()


@router.post("/", dependencies=[Depends(get_current_user)])
async def create_project(p: ProjectCreate, user=Depends(get_current_user)):
    coll = get_projects_collection()
    doc = p.dict()
    doc.update({"owner_id": str(user.id), "status": "running", "owner_telegram_chat_id": user.telegram_chat_id})
    res = await coll.insert_one(doc)
    doc["_id"] = res.inserted_id
    scheduler.start_project(doc)
    return {"id": str(doc["_id"]),
            "name": doc["name"],
            "type": doc["type"],
            "url": doc.get("url"),
            "interval_s": doc.get("interval_s"),
            "status": doc.get("status")}


@router.post("/{project_id}/stop", dependencies=[Depends(get_current_user)])
async def stop_project(project_id: str, user=Depends(get_current_user)):
    scheduler.stop_project(project_id)
    coll = get_projects_collection()
    await coll.update_one({
        "_id": ObjectId(project_id),
        "owner_id": str(user.id)},
        {
            "$set":
                {
                    "status": "stopped"
                }
        })
    return {"ok": True}


@router.post("/{project_id}/start", dependencies=[Depends(get_current_user)])
async def start_project(project_id: str, user=Depends(get_current_user)):
    coll = get_projects_collection()
    p = await coll.find_one({"_id": ObjectId(project_id), "owner_id": str(user.id)})
    if not p:
        raise HTTPException(404, "Project not found")
    await coll.update_one({
        "_id": ObjectId(project_id)},
        {
            "$set":
                {
                    "status": "running"
                }
        })
    scheduler.start_project(p)
    return {"ok": True}


@router.get("/{project_id}/errors", dependencies=[Depends(get_current_user)])
async def get_project_errors(project_id: str,
                             limit: int = Query(20, gt=0, le=100),
                             skip: int = 0, user=Depends(get_current_user)):
    coll = get_errors_collection()
    cursor = coll.find({
        "project_id": ObjectId(project_id),
        "owner_id": str(user.id)
    }).sort("timestamp", -1).skip(skip).limit(limit)
    out = []
    async for e in cursor:
        e['id'] = str(e['_id'])
        out.append(e)
    return out
