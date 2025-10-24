import asyncio
from typing import Dict
from app.db.mongo import get_projects_collection
from app.services.http_alerter import do_http_check

_tasks: Dict[str, asyncio.Task] = {}


async def _run_project_loop(project_doc):
    interval = project_doc.get("interval_s", 60)
    while True:
        ok = True
        if project_doc.get("type") == "HTTP":
            ok = await do_http_check(project_doc)

        coll = get_projects_collection()
        await coll.update_one(
            {"_id": project_doc["_id"]},
            {"$set": {"last_run_at": __import__("datetime").datetime.utcnow()}}
        )
        if not ok and project_doc.get("stop_on_error", True):
            await coll.update_one({"_id": project_doc["_id"]}, {"$set": {"status": "stopped"}})
            break
        await asyncio.sleep(interval)


def start_project(project_doc):
    pid = str(project_doc["_id"])
    if pid in _tasks:
        return
    task = asyncio.create_task(_run_project_loop(project_doc))
    _tasks[pid] = task


def stop_project(project_id: str):
    task = _tasks.pop(project_id, None)
    if task:
        task.cancel()


async def restore_running_projects():
    coll = get_projects_collection()
    async for proj in coll.find({"status": "running"}):
        start_project(proj)
