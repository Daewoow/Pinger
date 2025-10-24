import httpx
from typing import Dict, Any
from app.db.mongo import get_errors_collection, get_projects_collection


async def do_http_check(project: Dict[str, Any]):
    url = project.get("url")
    timeout = project.get("timeout_s", 10)
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.get(url, headers=project.get("headers") or {})
            if r.status_code >= 500:
                await record_error(project, f"HTTP {r.status_code}", status_code=r.status_code,
                                   response_time_ms=r.elapsed.total_seconds() * 1000)
                return False
            return True
    except Exception as e:
        await record_error(project, str(e))
    return False


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
