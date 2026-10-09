"""
  @Author:LiShuo
  @Time:2026/10/8
  @Desc:转换器，负责在两种实体之间互相转换数据，比如：

数据库层（MySQL 模型：ColumnInfoMySQL）

业务逻辑层（实体：ColumnInfo）
"""
from dataclasses import asdict

from app.entities.column_info import ColumnInfo
from app.models.column_info_mysql import ColumnInfoMySQL


class ColumnInfoMapper:

    @staticmethod
    def to_entity(column_info_mysql:ColumnInfoMySQL) -> ColumnInfo:
        # 将持久层对象 转为 业务层对象 只能手动赋值
        return ColumnInfo(
            id=column_info_mysql.id,
            name=column_info_mysql.name,
            type=column_info_mysql.type,
            role=column_info_mysql.role,
            examples=column_info_mysql.examples,
            description=column_info_mysql.description,
            alias=column_info_mysql.alias,
            table_id=column_info_mysql.table_id,
        )
    @staticmethod
    def to_model(column_info:ColumnInfo) -> ColumnInfoMySQL:
        # 将业务层对象转为持久层对象
        return ColumnInfoMySQL(**asdict(column_info))