from app.services.http_pinger import HttpPinger
from app.services.pinger import Pinger
from app.services.icmp_pinger import IcmpPinger
from app.services.tcp_pinger import TcpPinger
from typing import Optional


class PingerFactory:
    @staticmethod
    def create(type_: str) -> Optional[Pinger]:
        if type_ == "HTTP":
            return HttpPinger()
        elif type_ == "TCP":
            return TcpPinger()
        elif type_ == "ICMP":
            return IcmpPinger()
        return None
