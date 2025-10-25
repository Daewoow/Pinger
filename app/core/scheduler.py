import asyncio
from datetime import datetime, timezone
from typing import Dict

from bson import ObjectId

from app.db.mongo import get_projects_collection, get_errors_collection
from app.services.tg_notify import Notifier
from app.services.pinger_factory import PingerFactory

_tasks: Dict[str, asyncio.Task] = {}


async def _run_project_loop(project_doc):
    interval = project_doc.get("interval_s", 60)
    project_id = str(project_doc.get("_id"))
    projects_coll = get_projects_collection()
    errors_coll = get_errors_collection()

    while True:
        project = await projects_coll.find_one({"_id": ObjectId(project_id)})
        if not project or project.get("status") != "running":
            print(f"Project {project_id} stopped or not found, exiting loop")
            break

        error_message = None
        error_details = {}

        try:
            ttype = project_doc.get("type")
            pinger = PingerFactory.create(ttype)
            ok = await pinger.check(project_doc)
        except Exception as e:
            ok = False
            error_message = str(e)
            error_details = {"exception": type(e).__name__}
            print(f"Error in project {project_id}: {error_message}")

        await projects_coll.update_one(
            {"_id": ObjectId(project_id)},
            {"$set": {"last_run_at": datetime.now(tz=timezone.utc).isoformat()}}
        )

        if not ok and project_doc.get("stop_on_error", True):
            await errors_coll.insert_one({
                "_id": str(ObjectId()),
                "project_id": project_id,
                "timestamp": datetime.now(tz=timezone.utc).isoformat(),
                "error_message": error_message or "Check failed",
                "details": error_details
            })

            await projects_coll.update_one(
                {"_id": ObjectId(project_id)},
                {"$set": {"status": "stopped"}}
            )

            chat = project_doc.get("owner_telegram_chat_id")
            if chat:
                try:
                    await Notifier().send_telegram(
                        chat,
                        f"[Monitoring] Project {project_doc.get('name')} "
                        f"stopped due to error: {error_message or 'Check failed'}"
                    )
                except Exception as e:
                    print(f"Failed to send Telegram notification for project {project_id}: {e}")

            print(f"Project {project_id} stopped due to error")
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
