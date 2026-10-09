"""
  @Author:LiShuo
  @Time:2026/10/8
  @Desc:
"""
from dataclasses import dataclass
from typing import Any

@dataclass
class ColumnInfo:
  id: int  # 字段唯一标识ID
  name: str  # 字段名称（如 customer_name）
  type: str  # 字段数据类型（如 varchar、int、decimal）
  role: str  # 字段业务角色（primary_key / foreign_key / measure / dimension）
  examples: list  # 字段值示例（如 ["张三","李四"]，帮模型理解取值范围）
  description: str  # 字段业务描述（如 "客户名称"）
  alias: list  # 字段别名（如 ["客户名称","用户名称"]）
  table_id: str  # 所属表的唯一标识（关联表元数据）