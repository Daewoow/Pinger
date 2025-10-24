from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings


_mongo_client: AsyncIOMotorClient | None = None


def get_mongo_client() -> AsyncIOMotorClient:
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = AsyncIOMotorClient(settings.MONGO_URL)
    return _mongo_client


def get_projects_collection():
    return get_mongo_client().monitoring.projects


def get_errors_collection():
    return get_mongo_client().monitoring.errors
