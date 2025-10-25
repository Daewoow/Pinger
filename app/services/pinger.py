from abc import ABC, abstractmethod
from app.db.mongo import get_errors_collection
from typing import Dict, Any
from .tg_notify import Notifier


class Pinger(ABC):
    @abstractmethod
    async def alert(self, project):
        pass

    @staticmethod
    async def record_error(project: Dict[str, Any], error: str, status_code: int | None = None,
                           response_time_ms: float | None = None):
        errors = get_errors_collection()

        await errors.insert_one({
            "project_id": project["_id"],
            "owner_id": project["owner_id"],
            "timestamp": __import__("datetime").datetime.utcnow(),
            "type": project.get("type"),
            "status_code": status_code,
            "error": error,
            "response_time_ms": response_time_ms,
        })
        chat_id = project.get("owner_telegram_chat_id")
        if chat_id:
            try:
                await Notifier().send_telegram(chat_id, f"[Monitoring] Project {project.get('name')} error: {error}")
            except Exception:
                pass
