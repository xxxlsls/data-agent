"""
  @Author:LiShuo
  @Time:2026/10/8
  @Desc:
"""
from dataclasses import dataclass
from typing import Any

@dataclass
class ColumnInfo:
  id: str
  name: str
  type: str
  role: str
  examples: list[Any]
  description: str
  alias: list[str]
  table_id: str