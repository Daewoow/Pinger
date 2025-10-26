import httpx
from typing import Dict, Any
from .pinger import Pinger


class HttpPinger(Pinger):
    @Pinger.log_checking
    async def check(self, project: Dict[str, Any]):
        url = project.get("url")
        timeout = project.get("timeout_s", 10)
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                r = await client.get(url, headers=project.get("headers") or {})
                if r.status_code >= 500 or r.status_code == 404:
                    await self.alert_error(project, f"HTTP {r.status_code}", status_code=r.status_code,
                                           response_time_ms=r.elapsed.total_seconds() * 1000)
                    return False
                return True
        except Exception as e:
            await self.alert_error(project, str(e))
        return False
