from fastapi import APIRouter, Depends, HTTPException
from app.models.pydantic_models import ProjectCreate
from app.db.mongo import get_projects_collection, get_errors_collection
from app.core import scheduler
from app.core.auth import get_current_user
from bson import ObjectId

router = APIRouter()


@router.post("/", dependencies=[Depends(get_current_user)])
async def create_project(p: ProjectCreate, user=Depends(get_current_user)):
    coll = get_projects_collection()
    doc = p.dict(exclude_unset=True)
    if doc.get("url") is not None:
        doc["url"] = str(doc["url"])

    doc.update({
        "_id": str(ObjectId()),
        "owner_id": str(user.id),
        "status": "running",
        "owner_telegram_chat_id": user.telegram_chat_id or None
    })

    try:
        res = await coll.insert_one(doc)
        scheduler.start_project(doc)
        return {
            "id": str(res.inserted_id),
            "name": doc["name"],
            "type": doc["type"],
            "url": doc.get("url"),
            "interval_s": doc.get("interval_s"),
            "status": doc.get("status")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create project: {str(e)}")


@router.post("/{project_id}/stop", dependencies=[Depends(get_current_user)])
async def stop_project(project_id: str, user=Depends(get_current_user)):
    coll = get_projects_collection()
    try:
        result = await coll.update_one(
            {"_id": ObjectId(project_id), "owner_id": str(user.id)},
            {"$set": {"status": "stopped"}}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Project not found")
        scheduler.stop_project(project_id)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop project: {str(e)}")


@router.post("/{project_id}/start", dependencies=[Depends(get_current_user)])
async def start_project(project_id: str, user=Depends(get_current_user)):
    coll = get_projects_collection()
    p = await coll.find_one({"_id": ObjectId(project_id), "owner_id": str(user.id)})
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    await coll.update_one(
        {"_id": ObjectId(project_id)},
        {"$set": {"status": "running"}}
    )
    scheduler.start_project(p)
    return {"ok": True}


@router.get("/")
async def get_projects():
    coll = get_projects_collection()
    projects = coll.find({})
    return {"projects": [p async for p in projects]}


@router.delete("/")
async def delete_projects():
    coll = get_projects_collection()
    try:
        coll.delete_many({})
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)


@router.get("/{project_id}", summary="Информация о проекте")
async def get_project_info(project_id: str, user=Depends(get_current_user)):
    try:
        ObjectId(project_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid project_id: must be a 24-character hex string")

    projects_coll = get_projects_collection()
    errors_coll = get_errors_collection()

    project = await projects_coll.find_one({"_id": ObjectId(project_id), "owner_id": str(user.id)})
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")

    errors_cursor = errors_coll.find({"project_id": project_id}).sort("timestamp", -1).limit(50)
    return await get_answer(errors_cursor, project)


@router.get("/by-name/{project_name}", summary="Информация о проекте по имени")
async def get_project_by_name(project_name: str, user=Depends(get_current_user)):
    projects_coll = get_projects_collection()
    errors_coll = get_errors_collection()

    project = await projects_coll.find_one({"name": project_name, "owner_id": str(user.id)})
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")

    errors_cursor = errors_coll.find({"project_id": str(project["_id"])}).sort("timestamp", -1).limit(50)
    return await get_answer(errors_cursor, project)


async def get_answer(errors_cursor, project):
    errors = [err async for err in errors_cursor]
    return {
        "project": {
            "id": str(project["_id"]),
            "name": project["name"],
            "type": project["type"],
            "url": project.get("url"),
            "host": project.get("host"),
            "port": project.get("port"),
            "headers": project.get("headers", {}),
            "interval_s": project.get("interval_s"),
            "timeout_s": project.get("timeout_s"),
            "stop_on_error": project.get("stop_on_error"),
            "status": project.get("status")
        },
        "errors": [
            {
                "id": str(err["_id"]),
                "project_id": err["project_id"],
                "timestamp": err.get("timestamp"),
                "error_message": err.get("error_message"),
                "details": err.get("details", {})
            } for err in errors
        ]
    }
