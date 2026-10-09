"""
  @Author:LiShuo
  @Time:2026/10/8
  @Desc:
"""
from dataclasses import dataclass

@dataclass
class TableInfo:
    id: str
    name: str
    role: str
    description: str