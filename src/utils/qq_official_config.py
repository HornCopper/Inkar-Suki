"""项目 YAML 配置到 NoneBot QQ 适配器配置的转换。"""

from typing import Any

from pydantic import BaseModel, Field, SecretStr, field_validator


class QQOfficialConfig(BaseModel):
    enabled: bool = False
    app_id: str = ""
    app_secret: SecretStr = Field(default = SecretStr(""), repr = False)
    use_websocket: bool = False
    driver: str = "~fastapi+~httpx+~websockets"

    @field_validator("app_id", mode = "before")
    @classmethod
    def normalize_app_id(cls, value: Any) -> str:
        return str(value).strip() if isinstance(value, (str, int)) else value

    def nonebot_options(self) -> dict[str, Any]:
        if not self.enabled:
            return {}
        secret = self.app_secret.get_secret_value()
        if not self.app_id or not secret.strip():
            raise ValueError("请填写 src/config/config.yml 中 qq_official 的 app_id 和 app_secret，再启用 QQ 官方接入。")
        return {
            "driver": self.driver,
            "qq_verify_webhook": True,
            "qq_bots": [{
                "id": self.app_id,
                "secret": secret,
                "use_websocket": self.use_websocket,
                "intent": {
                    "guilds": False,
                    "guild_members": False,
                    "guild_message_reactions": False,
                    "message_audit": False,
                    "at_messages": False,
                    "c2c_group_at_messages": True,
                },
            }],
        }
