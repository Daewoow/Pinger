import logging

from abc import ABC, abstractmethod
from app.db.mongo import get_errors_collection
from functools import wraps
from typing import Dict, Any
from .tg_notify import Notifier


class Pinger(ABC):
    @abstractmethod
    async def check(self, project):
        pass

    @staticmethod
    def log_checking(func):
        @wraps(func)
        async def wrapper(self: Pinger, projects: Dict[str, Any], *args, **kwargs):
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            logger = logging.getLogger(self.__class__.__name__)
            logger.info(f"{self.__class__.__name__} checking {projects.get('name')}; Id {projects.get('_id')}")
            return await func(self, projects, *args, **kwargs)
        return wrapper

    @staticmethod
    async def alert_error(project: Dict[str, Any], error: str, status_code: int | None = None,
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
                await Notifier().send_telegram(chat_id, f"[Monitoring] Project {project.get('name')};\n"
                                                        f"Host: {project.get('host')};\n"
                                                        f"Url: {project.get('url')};\n"
                                                        f"Host error: {error}")
            except Exception:
                pass
