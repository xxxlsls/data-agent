"""
  @Author:LiShuo
  @Time:2026/10/8
  @Desc:
"""
from dataclasses import dataclass

@dataclass
class ValueInfo:
  id: str
  value: str
  column_id: str