"""
  @Author:LiShuo
  @Time:2026/10/8
  @Desc:
"""
from dataclasses import dataclass

@dataclass
class MetricInfo:
  id: str
  name: str
  description: str
  relevant_columns: list[str]
  alias: list[str]