from typing import Tuple, Literal

from src.config import Config
from src.utils.network import Request

import socket
import time

def tcping(host, port, timeout=3):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, port))
        return True
    except (socket.timeout, socket.error) as e:
        return False
    finally:
        sock.close()


async def get_server_status(_server: str = "") -> str:
    servers = (await Request("https://spider2.jx3box.com/api/spider/server/server_state").get()).json()
    for server in servers:
        if server["server_name"] == _server:
            status = tcping(server["ip_address"], int(server["ip_port"]), 1)
            if not status:
                return f"{_server} 维护中。"
            return f"{_server} 开服中。"
    raise ValueError(f"Cannot recognize the server {_server}!")