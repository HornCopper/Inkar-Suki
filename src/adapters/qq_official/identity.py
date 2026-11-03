"""兼容原有导入路径；身份存储也供 OneBot 管理命令使用。"""

from src.utils.identity import IdentityStore

__all__ = ["IdentityStore"]
