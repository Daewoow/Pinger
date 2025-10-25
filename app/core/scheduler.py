import asyncio
from typing import Dict
from app.db.mongo import get_projects_collection
from app.services.tg_notify import Notifier
from app.services.pinger_factory import PingerFactory

_tasks: Dict[str, asyncio.Task] = {}


async def _run_project_loop(project_doc):
    interval = project_doc.get("interval_s", 60)
    project_id = str(project_doc.get("_id"))
    coll = get_projects_collection()
    while True:
        ok = True
        ttype = project_doc.get("type")
        alerter = PingerFactory.create(ttype)
        await alerter.alert(project_doc)
        await coll.update_one(
            {"_id": project_id},
            {"$set": {"last_run_at": __import__("datetime").datetime.utcnow()}}
        )
        if not ok and project_doc.get("stop_on_error", True):
            await coll.update_one(
                {"_id": project_id},
                {"$set": {"status": "stopped"}}
            )

            chat = project_doc.get("owner_telegram_chat_id")
            if chat:
                try:
                    await Notifier().send_telegram(
                        chat,
                        f"[Monitoring] Project {project_doc.get('name')} stopped due to error"
                    )
                except Exception:
                    pass
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
