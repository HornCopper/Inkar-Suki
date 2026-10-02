import ipaddress
import re
from dataclasses import dataclass

from mcstatus import BedrockServer, JavaServer


GAME_MODE_NAMES = {
    "survival": "生存",
    "creative": "创造",
    "adventure": "冒险",
    "spectator": "旁观",
}
QUERY_TIMEOUT = 5


@dataclass(frozen=True)
class ServerAddress:
    host: str
    port: int
    port_was_given: bool

    @property
    def lookup_target(self) -> str:
        host = f"[{self.host}]" if ":" in self.host else self.host
        if self.port_was_given:
            return f"{host}:{self.port}"
        return host

    @property
    def display(self) -> str:
        host = f"[{self.host}]" if ":" in self.host else self.host
        return f"{host}:{self.port}"


def clean(string: str) -> str:
    """移除文本中的 Minecraft 旧版格式代码。"""
    return re.sub(r"§[0-9A-FK-ORX]", "", str(string), flags=re.IGNORECASE).strip()


def _parse_address(raw_address: str, default_port: int) -> ServerAddress:
    address = raw_address.strip()
    if not address:
        raise ValueError("地址不能为空")
    if any(char.isspace() for char in address) or any(char in address for char in "/?#@"):
        raise ValueError("地址中包含无效字符")

    port_was_given = False
    if address.startswith("["):
        match = re.fullmatch(r"\[([^]]+)](?::([^:]+))?", address)
        if match is None:
            raise ValueError("IPv6 地址格式有误")
        host, raw_port = match.groups()
        try:
            ipaddress.IPv6Address(host)
        except ValueError as exc:
            raise ValueError("IPv6 地址格式有误") from exc
        port_was_given = raw_port is not None
    elif address.count(":") > 1:
        try:
            ipaddress.IPv6Address(address)
        except ValueError as exc:
            raise ValueError("地址格式有误；IPv6 指定端口时请使用 [地址]:端口") from exc
        host, raw_port = address, None
    elif ":" in address:
        host, raw_port = address.rsplit(":", 1)
        port_was_given = True
    else:
        host, raw_port = address, None

    host = host.strip()
    if not host or len(host) > 253:
        raise ValueError("主机名格式有误")

    if raw_port is None:
        port = default_port
    else:
        try:
            port = int(raw_port)
        except (TypeError, ValueError) as exc:
            raise ValueError("端口必须是数字") from exc
        if not 1 <= port <= 65535:
            raise ValueError("端口必须在 1 到 65535 之间")

    return ServerAddress(host=host, port=port, port_was_given=port_was_given)


def _format_status(address: ServerAddress, status, *, bedrock: bool) -> str:
    edition = "基岩版" if bedrock else "Java 版"
    motd = status.motd.to_plain().strip() or "无"
    lines = [
        f"已经查到{edition}服务器啦：",
        f"地址：{address.display}",
        f"在线人数：{status.players.online}/{status.players.max}",
        f"版本：{clean(status.version.name)}",
    ]

    if bedrock and status.gamemode:
        game_mode = clean(status.gamemode)
        lines.append(f"游戏模式：{GAME_MODE_NAMES.get(game_mode.lower(), game_mode)}")

    lines.extend((f"延迟：{status.latency:.0f} ms", f"介绍：{motd}"))
    return "\n".join(lines)


async def _query_server(raw_address: str, *, bedrock: bool) -> str:
    edition = "基岩版" if bedrock else "Java 版"
    default_port = 19132 if bedrock else 25565
    try:
        address = _parse_address(raw_address, default_port)
    except ValueError as exc:
        return f"地址输入有误：{exc}。"

    try:
        if bedrock:
            server = BedrockServer(address.host, address.port, timeout=QUERY_TIMEOUT)
        elif address.port_was_given:
            server = JavaServer(address.host, address.port, timeout=QUERY_TIMEOUT)
        else:
            # Java 客户端会在未指定端口时查询 _minecraft._tcp SRV 记录。
            server = await JavaServer.async_lookup(address.host, timeout=QUERY_TIMEOUT)
        status = await server.async_status(tries=1)
    except Exception:
        return (
            f"未查询到{edition}服务器：{address.display}\n"
            "服务器可能离线、无法从机器人所在网络访问，或地址、端口不正确。"
        )

    return _format_status(address, status, bedrock=bedrock)


async def get_java_server(raw_ip: str) -> str:
    return await _query_server(raw_ip, bedrock=False)


async def get_bedrock_server(raw_ip: str) -> str:
    return await _query_server(raw_ip, bedrock=True)
