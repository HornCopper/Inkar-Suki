# TODO 使用数据库存储
class BaseCatalog:
    """基础目录"""

    """目录全名"""
    id: str = None
    """名称"""
    name: str = None
    """描述"""
    description: str = None
    """是否显示"""
    visiable: bool = True
    """是否启用"""
    enable: bool = True
    """菜单中显示的优先级"""
    priority: int = 0
    """路径"""
    path: str = None

    @classmethod
    def mark(cls, *args, **kwargs):
        """标注"""
        for x in kwargs:
            setattr(cls, x, kwargs[x])

    @classmethod
    def tostring(cls):
        return f"[{cls.name}]enable:{cls.enable},visiable:{cls.visiable}"

    @classmethod
    def to_dict(cls):
        return {
            "name": cls.name,
            "description": cls.description,
            "visiable": cls.visiable,
            "enable": cls.enable,
            "priority": cls.priority,
            "children": [x.to_dict() for x in cls.children] if hasattr(cls, "children") else [],
            "path": cls.path,
        }
