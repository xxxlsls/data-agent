"""
  @Author:LiShuo
  @Time:2026/10/9
  @Desc:定义总的langgraph图
"""
from langgraph.graph import StateGraph


def build_graph():

    # 创建图构建器
    graph = StateGraph()