from nonebot import get_plugin_config
from pydantic import BaseModel


class Config(BaseModel):
    handle_strict_mode: bool = False
    handle_color_enhance: bool = False


handle_config = get_plugin_config(Config)
