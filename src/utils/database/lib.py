"""
本文件无需遵守 AGPLv3 协议。
原作者：@Snowykami
本文件按原始仓库：LiteyukiStudio/LiteyukiBot
"""
from typing import Any, Callable, List, TypeVar
from packaging.version import parse
from pydantic import BaseModel

import os
import pickle
import sqlite3
import inspect
import pydantic

T = TypeVar("T")

NoneType = type(None)

class LiteModel(BaseModel):
    TABLE_NAME: str | None = None
    id: int | None = None

    def dump(self, *args, **kwargs):
        
        if parse(pydantic.__version__) < parse("2.0.0"):
            return self.dict(*args, **kwargs)
        else:
            return self.model_dump(*args, **kwargs)


class Database:
    def __init__(self, db_name: str):

        if os.path.dirname(db_name) != "" and not os.path.exists(os.path.dirname(db_name)):
            os.makedirs(os.path.dirname(db_name))

        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

        self._on_save_callbacks = []

    def where_one(self, model: LiteModel, condition: str = "", *args: Any, default: T = None) -> LiteModel | T | None:
        """查询第一个
        Args:
            model: 数据模型实例
            condition: 查询条件，不给定则查询所有
            *args: 参数化查询参数
            default: 默认值

        Returns:

        """
        all_results = self.where_all(model, condition, *args)
        return all_results[0] if all_results else default

    def where_all(self, model: LiteModel, condition: str = "", *args: Any, default: T = None) -> List[LiteModel | T] | T | None:
        """查询所有
        Args:
            model: 数据模型实例
            condition: 查询条件，不给定则查询所有
            *args: 参数化查询参数
            default: 默认值

        Returns:

        """
        table_name = model.TABLE_NAME
        model_type = type(model)
        if not table_name:
            raise ValueError(f"数据模型{model_type.__name__}未提供表名")
        if condition:
            results = self.cursor.execute(f"SELECT * FROM {table_name} WHERE {condition}", args).fetchall()
        else:
            results = self.cursor.execute(f"SELECT * FROM {table_name}").fetchall()
        fields = [description[0] for description in self.cursor.description]
        if not results:
            return default
        else:
            return [model_type(**self._load(dict(zip(fields, result)))) for result in results]

    def save(self, *args: LiteModel) -> None:
        """增/改操作
        Args:
            *args:
        Returns:
        """
        table_list = [item[0] for item in self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        for model in args:
            if not model.TABLE_NAME:
                raise ValueError(f"数据模型 {model.__class__.__name__} 未提供表名")
            elif model.TABLE_NAME not in table_list:
                raise ValueError(f"数据模型 {model.__class__.__name__} 表 {model.TABLE_NAME} 不存在，请先迁移")
            else:
                self._save(model.dump(by_alias=True))

            for callback in self._on_save_callbacks:
                callback(model)

    def _save(self, obj: Any) -> Any:
        
        if isinstance(obj, dict):
            table_name = obj.get("TABLE_NAME")
            row_id = obj.get("id")
            new_obj = {}
            for field, value in obj.items():
                if isinstance(value, self.ITERABLE_TYPE):
                    new_obj[self._get_stored_field_prefix(value) + field] = self._save(value)  
                elif isinstance(value, self.BASIC_TYPE):
                    new_obj[field] = value
                else:
                    raise ValueError(f"数据模型{table_name}包含不支持的数据类型，字段：{field} 值：{value} 值类型：{type(value)}")
            if table_name:
                fields, values = [], []
                for n_field, n_value in new_obj.items():
                    if n_field not in ["TABLE_NAME", "id"]:
                        fields.append(n_field)
                        values.append(n_value)
                
                fields = list(fields)
                values = list(values)
                if row_id is not None:
                    
                    fields.insert(0, 'id')
                    
                    values.insert(0, row_id)
                fields = ', '.join([f'"{field}"' for field in fields])
                placeholders = ', '.join('?' for _ in values)
                self.cursor.execute(f"INSERT OR REPLACE INTO {table_name}({fields}) VALUES ({placeholders})", tuple(values))
                self.conn.commit()
                foreign_id = self.cursor.execute("SELECT last_insert_rowid()").fetchone()[0]
                return f"{self.FOREIGN_KEY_PREFIX}{foreign_id}@{table_name}"  
            else:
                return pickle.dumps(new_obj)  
        elif isinstance(obj, (list, set, tuple)):
            obj_type = type(obj)  
            new_obj = []
            for item in obj:
                if isinstance(item, self.ITERABLE_TYPE):
                    new_obj.append(self._save(item))
                elif isinstance(item, self.BASIC_TYPE):
                    new_obj.append(item)
                else:
                    raise ValueError(f"数据模型包含不支持的数据类型，值：{item} 值类型：{type(item)}")
            return pickle.dumps(obj_type(new_obj))  
        else:
            raise ValueError(f"数据模型包含不支持的数据类型，值：{obj} 值类型：{type(obj)}")

    def _load(self, obj: Any) -> Any:

        if isinstance(obj, dict):

            new_obj = {}

            for field, value in obj.items():

                field: str

                if field.startswith(self.BYTES_PREFIX):
                    if isinstance(value, bytes):
                        new_obj[field.replace(self.BYTES_PREFIX, "")] = self._load(pickle.loads(value))
                    else:  
                        pass
                        

                elif field.startswith(self.FOREIGN_KEY_PREFIX):

                    new_obj[field.replace(self.FOREIGN_KEY_PREFIX, "")] = self._load(self._get_foreign_data(value))

                else:
                    new_obj[field] = value
            return new_obj
        elif isinstance(obj, (list, set, tuple)):

            new_obj = []
            for item in obj:

                if isinstance(item, bytes):

                    
                    try:
                        new_obj.append(self._load(pickle.loads(item)))
                    except Exception:
                        new_obj.append(self._load(item))

                elif isinstance(item, str) and item.startswith(self.FOREIGN_KEY_PREFIX):
                    new_obj.append(self._load(self._get_foreign_data(item)))
                else:
                    new_obj.append(self._load(item))
            return new_obj
        else:
            return obj

    def delete(self, model: LiteModel, condition: str, *args: Any, allow_empty: bool = False) -> None:
        """
        删除满足条件的数据
        Args:
            allow_empty: 允许空条件删除整个表
            model:
            condition:
            *args:

        Returns:

        """
        table_name = model.TABLE_NAME
        if not table_name:
            raise ValueError(f"数据模型{model.__class__.__name__}未提供表名")
        if model.id is not None:
            condition = f"id = {model.id}"
        if not condition and not allow_empty:
            raise ValueError("删除操作必须提供条件")
        self.cursor.execute(f"DELETE FROM {table_name} WHERE {condition}", args)
        self.conn.commit()

    def auto_migrate(self, *args: LiteModel) -> None:

        """
        自动迁移模型
        Args:
            *args: 模型类实例化对象，支持空默认值，不支持嵌套迁移

        Returns:

        """
        for model in args:
            if not model.TABLE_NAME:
                raise ValueError(f"数据模型{type(model).__name__}未提供表名")

            
            self.cursor.execute(
                f'CREATE TABLE IF NOT EXISTS "{model.TABLE_NAME}" (id INTEGER PRIMARY KEY AUTOINCREMENT)'
            )

            
            new_structure = {}
            for n_field, n_value in model.dump(by_alias=True).items():
                if n_field not in ["TABLE_NAME", "id"]:
                    new_structure[self._get_stored_field_prefix(n_value) + n_field] = self._get_stored_type(n_value)

            
            existing_structure = dict([(column[1], column[2]) for column in self.cursor.execute(f'PRAGMA table_info({model.TABLE_NAME})').fetchall()])
            
            for n_field, n_type in new_structure.items():
                if n_field not in existing_structure.keys() and n_field.lower() not in ["id", "table_name"]:
                    default_value = self.DEFAULT_MAPPING.get(n_type, 'NULL')
                    self.cursor.execute(
                        f"ALTER TABLE '{model.TABLE_NAME}' ADD COLUMN {n_field} {n_type} DEFAULT {self.DEFAULT_MAPPING.get(n_type, default_value)}"
                    )

            
            for e_field in existing_structure.keys():
                if e_field not in new_structure.keys() and e_field.lower() not in ['id']:
                    self.cursor.execute(
                        f'ALTER TABLE "{model.TABLE_NAME}" DROP COLUMN "{e_field}"'
                    )
        self.conn.commit()
        

    def _get_stored_field_prefix(self, value) -> str:
        """根据类型获取存储字段前缀，一定在后加上字段名
        * -> ""
        Args:
            value: 储存的值

        Returns:
            Sqlite3存储字段
        """

        if isinstance(value, LiteModel) or isinstance(value, dict) and "TABLE_NAME" in value:
            return self.FOREIGN_KEY_PREFIX
        elif type(value) in self.ITERABLE_TYPE:
            return self.BYTES_PREFIX
        return ""

    def _get_stored_type(self, value) -> str:
        """获取存储类型

        Args:
            value: 储存的值

        Returns:
            Sqlite3存储类型
        """
        if isinstance(value, dict) and "TABLE_NAME" in value:
            
            return "INTEGER"
        return self.TYPE_MAPPING.get(type(value), "TEXT")

    def _get_foreign_data(self, foreign_value: str) -> dict:
        """
        获取外键数据
        Args:
            foreign_value:

        Returns:

        """
        foreign_value = foreign_value.replace(self.FOREIGN_KEY_PREFIX, "")
        table_name = foreign_value.split("@")[-1]
        foreign_id = foreign_value.split("@")[0]
        fields = [description[1] for description in self.cursor.execute(f"PRAGMA table_info({table_name})").fetchall()]
        result = self.cursor.execute(f"SELECT * FROM {table_name} WHERE id = ?", (foreign_id,)).fetchone()
        return dict(zip(fields, result))

    def on_save(self, func: Callable[[LiteModel, Any], None]):
        """
        装饰一个可调用对象使其在储存数据模型时被调用
        Args:
            func:
        Returns:
        """

        def wrapper(model: LiteModel):
            
            sign = inspect.signature(func)
            if param := sign.parameters.get("model"):
                if isinstance(model, param.annotation):
                    pass
                else:
                    return
            else:
                return
            result = func(model) # type: ignore
            for callback in self._on_save_callbacks:
                callback(result)
            return result

        self._on_save_callbacks.append(wrapper)
        return wrapper

    TYPE_MAPPING = {
            int      : "INTEGER",
            float    : "REAL",
            str      : "TEXT",
            bool     : "INTEGER",
            bytes    : "BLOB",
            NoneType : "NULL",
            dict     : "BLOB",  
            list     : "BLOB",  
            tuple    : "BLOB",  
            set      : "BLOB",  
            LiteModel: "TEXT"  
    }
    DEFAULT_MAPPING = {
            "TEXT"   : "''",
            "INTEGER": 0,
            "REAL"   : 0.0,
            "BLOB"   : None,
            "NULL"   : None
    }

    
    BASIC_TYPE = (int, float, str, bool, bytes, NoneType)
    
    ITERABLE_TYPE = (dict, list, tuple, set, LiteModel)

    
    FOREIGN_KEY_PREFIX = "FOREIGN_KEY_"
    
    BYTES_PREFIX = "PICKLE_BYTES_"