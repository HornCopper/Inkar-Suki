from pydantic import BaseModel
import yaml
import os

class BotBasic(BaseModel):
    bot_name: str
    bot_name_argument: str
    bot_owner: list[str]
    bot_repo: str
    bot_notice: dict[str, str]
    proxy: str = ""

class GitHubConfig(BaseModel):
    web_path: str
    github_personal_token: str = ""

class Jx3API(BaseModel):
    token: str
    token_v2: str = ""
    ticket: str
    url: str

class Jx3WS(BaseModel):
    url: str
    token: str = ""

class Jx3Config(BaseModel):
    api: Jx3API
    ws: Jx3WS

class Hidden(BaseModel):
    offcial_token: str = ""

class config(BaseModel):
    bot_basic: BotBasic
    github: GitHubConfig
    jx3: Jx3Config
    hidden: Hidden

    @classmethod
    def from_yaml(cls, yaml_str: str) -> "config":
        config_data = yaml.safe_load(yaml_str)
        return cls(**config_data)

script_dir = os.path.dirname(os.path.abspath(__file__))
yaml_file_path = os.path.join(script_dir, "config.yml")

with open(yaml_file_path, "r", encoding="utf8") as f:
    Config = config.from_yaml(f.read())