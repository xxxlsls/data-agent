"""
  @Author:LiShuo
  @Time:2026/10/9
  @Desc:
"""
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from typing_extensions import TypedDict

from app.repositories.es.value_es_repository import ValueESRepository
from app.repositories.mysql.dw.dw_mysql_repository import DWMySQLRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMySQLRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository


class DataAgentContext(TypedDict):
    """提供给节点需要使用依赖对象：查询数据库、向量库持久层对象"""
    dw_mysql_repository: DWMySQLRepository #mysql数据库

    embedding_client: HuggingFaceEndpointEmbeddings  # 向量服务器客户端

    column_qdrant_repository: ColumnQdrantRepository  # 字段向量库

    value_es_repository: ValueESRepository  # 字段值索引库

    metric_qdrant_repository: MetricQdrantRepository  # 指标向量库

    meta_mysql_repository: MetaMySQLRepository  # 元数据库