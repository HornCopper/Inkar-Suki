from pydantic import BaseModel

from src.const.path import CONFIG, build_path

import yaml

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
    xsk_secret: str = ""
    sign_secret: str = ""
    enable: bool = False
    weibo: bool = False
    calculator_url: str = ""
    bla_url: str = ""
    cqc_url: str = ""


class Jx3WS(BaseModel):
    url: str
    token: str = ""
    enable: bool = False


class Jx3Config(BaseModel):
    api: Jx3API
    ws: Jx3WS

class QWeather(BaseModel):
    url: str
    token: str

class Hidden(BaseModel):
    offcial_token: str = ""

class LLMProvider(BaseModel):
    """LLM 提供商配置"""
    name: str  # 提供商名称（自定义标识）
    protocol: str  # "openai" | "anthropic" | "google"
    api_key: str
    base_url: str = ""

class LLMModelRef(BaseModel):
    """LLM 模型引用配置"""
    name: str  # 模型名称
    provider: str  # 引用的提供商名称
    timeout: int = 30

class LLMConfig(BaseModel):
    enable: bool = False
    max_timeout: int = 300
    providers: list[LLMProvider] = []
    models: list[LLMModelRef] = []

class config(BaseModel):
    bot_basic: BotBasic
    github: GitHubConfig
    jx3: Jx3Config
    weather: QWeather
    hidden: Hidden
    llm: LLMConfig = LLMConfig()

    @classmethod
    def from_yaml(cls, yaml_str: str) -> "config":
        config_data = yaml.safe_load(yaml_str)
        return cls(**config_data)


LLM_CONFIG_TEMPLATE = """
llm: # LLM 自然语言理解配置
    enable: False # 是否启用 LLM 功能
    max_timeout: 300 # 最高超时时间（秒），所有模型请求累计不超过此值
    providers: # 提供商列表，定义 API 连接信息
        - name: "openai" # 提供商名称
          protocol: "openai" # 协议类型: openai / anthropic / google
          api_key: "" # API 密钥
          base_url: "" # 自定义端点，留空使用官方默认地址
    models: # 模型列表，请求随机分配，失败自动降级到下一个
        - name: "gpt-4o-mini" # 模型名称
          provider: "openai" # 引用上方定义的提供商
          timeout: 30 # 单次请求超时（秒）
"""

def migrate_config(config_path: str) -> None:
    """检查配置文件，若缺失 llm 段则自动追加"""
    with open(config_path, "r", encoding="utf8") as f:
        content = f.read()
        config_data = yaml.safe_load(content)
    
    if config_data is None:
        return
    
    if "llm" not in config_data:
        with open(config_path, "a", encoding="utf8") as f:
            f.write(LLM_CONFIG_TEMPLATE)

config_path = build_path(CONFIG, ["config.yml"])
migrate_config(config_path)

with open(config_path, "r", encoding="utf8") as f:
    Config = config.from_yaml(f.read())
