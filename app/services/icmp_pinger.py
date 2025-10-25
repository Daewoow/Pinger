import asyncio
import sys
from .pinger import Pinger
from typing import Dict, Any


class IcmpPinger(Pinger):
    async def check(self, project: Dict[str, Any]):
        target = project.get("host") or project.get("url")

        timeout = project.get("timeout_s", 5)
        if sys.platform.startswith("win"):
            cmd = ["ping", "-n", "1", "-w", str(int(timeout * 1000)), target]
        else:
            cmd = ["ping", "-c", "1", "-W", str(int(timeout)), target]
        try:
            proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE,
                                                        stderr=asyncio.subprocess.PIPE)
            out, err = await asyncio.wait_for(proc.communicate(), timeout=timeout + 2)
            rc = proc.returncode
            if rc == 0:
                return True
            else:
                await self.alert_error(project, f"ping rc={rc} stdout={out.decode()[:200]}")
            return False
        except Exception as e:
            await self.alert_error(project, str(e))
        return False
