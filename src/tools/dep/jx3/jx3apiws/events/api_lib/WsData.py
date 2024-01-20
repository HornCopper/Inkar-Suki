from pydantic import BaseModel


class WsData(BaseModel):
    """
    ws数据模型
    """

    action: int
    """ws消息类型"""
    data: dict
    """消息数据"""
