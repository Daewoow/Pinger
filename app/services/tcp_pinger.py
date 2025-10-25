import asyncio
from .pinger import Pinger
from typing import Dict, Any


class TcpPinger(Pinger):
    async def alert(self, project: Dict[str, Any]):
        host = project.get("host") or project.get("url")
        port = project.get("port") or 80
        timeout = project.get("timeout_s", 10)
        try:
            conn = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=timeout)
            reader, writer = conn
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass
            return True
        except Exception as e:
            await self.record_error(project, str(e))
        return False
