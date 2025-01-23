from src.utils.database.operation import get_group_settings

from .constant import server_aliases_data, server_zones_mapping_data


class Server:
    server_aliases: dict[str, list[str]] = server_aliases_data
    server_zones_mapping: dict[str, list[str]] = server_zones_mapping_data

    def __init__(self, server_name: str | None = None, group_id: int | None = None):
        self._server = server_name
        self.group_id = group_id

    @property
    def server_raw(self) -> str | None:
        data = self.server_aliases
        for server_name in data:
            if self._server == server_name or self._server in data[server_name]:
                return server_name
        return None

    @property
    def server(self) -> str | None:
        """
        服务器实际名称。

        如果初始化传入错误的服务器名且没有传入群号，或传入的群号也没有绑定服务器，那么本值为`None`。
        """
        if self._server is None and self.group_id is not None:
            final_server = get_group_settings(self.group_id, "server") or None
        elif self._server is not None:
            final_server = self.server_raw
            if final_server is None and self.group_id:
                final_server = get_group_settings(self.group_id, "server") or None
        else:
            final_server = None
        return final_server

    @property
    def zone_legacy(self) -> str | None:
        data = self.server_zones_mapping
        for zone_name in data:
            if self.server in data[zone_name]:
                return zone_name
        return None

    @property
    def zone(self) -> str | None:
        zone_legacy_name = self.zone_legacy
        if zone_legacy_name is None:
            return None
        return (
            zone_legacy_name
            if zone_legacy_name == "无界区"
            else zone_legacy_name[:2] + "区"
        )
