"""
  @Author:LiShuo
  @Time:2026/10/9
  @Desc:定义总的langgraph图
"""
import asyncio

from langgraph.constants import START, END
from langgraph.graph import StateGraph

from app.agent.context import DataAgentContext
from app.agent.nodes.add_extra_context import add_extra_context
from app.agent.nodes.correct_sql import correct_sql
from app.agent.nodes.execute_sql import execute_sql
from app.agent.nodes.filter_metric import filter_metric
from app.agent.nodes.filter_table import filter_table
from app.agent.nodes.generate_sql import generate_sql
from app.agent.nodes.merge_retrieved_info import merge_retrieved_info
from app.agent.nodes.recall_column import recall_column
from app.agent.nodes.recall_metric import recall_metric
from app.agent.nodes.recall_value import recall_value
from app.agent.nodes.validate_sql import validate_sql
from app.agent.nodes.extract_keywords import extract_keywords
from app.agent.state import DataAgentState
from app.clients.embedding_client_manager import embedding_client_manager
from app.clients.es_client_manager import es_client_manager
from app.clients.mysql_client_manager import meta_mysql_client_manager, dw_mysql_client_manager
from app.clients.qdrant_client_manager import qdrant_client_manager
from app.repositories.es.value_es_repository import ValueESRepository
from app.repositories.mysql.dw.dw_mysql_repository import DWMySQLRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMySQLRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository

# SQL校正的最大轮数,超过则直接执行,避免 validate_sql -> correct_sql 无限回环
MAX_CORRECT = 3


def _route_after_validate(state: DataAgentState) -> str:
    """校验通过、或校正次数已用尽 -> 执行SQL;否则去校正SQL"""
    if state.get("error") is None:
        return "execute_sql"
    if state.get("correct_count", 0) >= MAX_CORRECT:
        return "execute_sql"
    return "correct_sql"


def build_graph():
    """构建图并编译，返回 CompiledStateGraph"""
    # 创建图构建器：state_schema 存流动数据，context_schema 存静态依赖
    graph_builder = StateGraph(state_schema=DataAgentState, context_schema=DataAgentContext)

    # 添加节点
    graph_builder.add_node('add_extra_context',add_extra_context)
    graph_builder.add_node('correct_sql', correct_sql)
    graph_builder.add_node('execute_sql', execute_sql)
    graph_builder.add_node('extract_keywords', extract_keywords)
    graph_builder.add_node('filter_metric', filter_metric)
    graph_builder.add_node('filter_table', filter_table)
    graph_builder.add_node('generate_sql', generate_sql)
    graph_builder.add_node('merge_retrieved_info', merge_retrieved_info)
    graph_builder.add_node('recall_column', recall_column)
    graph_builder.add_node('recall_metric', recall_metric)
    graph_builder.add_node('recall_value', recall_value)
    graph_builder.add_node('validate_sql', validate_sql)

    # 添加边
    graph_builder.add_edge(START, 'extract_keywords')#提取关键字

    graph_builder.add_edge('extract_keywords', 'recall_column')#字段信息召回
    graph_builder.add_edge('extract_keywords', 'recall_metric')#指标信息召回
    graph_builder.add_edge('extract_keywords', 'recall_value')#字段值召回

    graph_builder.add_edge('recall_column', 'merge_retrieved_info')#合并召回信息
    graph_builder.add_edge('recall_metric', 'merge_retrieved_info')
    graph_builder.add_edge('recall_value', 'merge_retrieved_info')

    graph_builder.add_edge('merge_retrieved_info', 'filter_table')#过滤表信息
    graph_builder.add_edge('merge_retrieved_info', 'filter_metric')#过滤指标信息

    graph_builder.add_edge('filter_table', 'add_extra_context')#添加额外上下文信息
    graph_builder.add_edge('filter_metric', 'add_extra_context')

    graph_builder.add_edge('add_extra_context', 'generate_sql')#生成SQL

    graph_builder.add_edge('generate_sql', 'validate_sql')  # 校验SQL

    graph_builder.add_conditional_edges('validate_sql',lambda state:'execute_sql' if state['error'] is None else 'correct_sql' ,
                                        {"execute_sql":"execute_sql","correct_sql":"correct_sql"})#校正SQL

    graph_builder.add_edge("correct_sql", "validate_sql")#设置最大校正次数,不能进入死循环

    # graph_builder.add_edge("correct_sql", "execute_sql")#执行SQL

    graph_builder.add_edge("execute_sql", END)

    # 编译图
    return graph_builder.compile()


if __name__ == '__main__':
    graph = build_graph()
    # 查看图构建的形状
    # print(graph.get_graph().draw_mermaid())

    #初始化客户端对象
    embedding_client_manager.init()
    qdrant_client_manager.init()
    es_client_manager.init()
    meta_mysql_client_manager.init()
    dw_mysql_client_manager.init()


    async def test_graph():
        state = DataAgentState(query="统计2025年各地区销售总额")
        async with (meta_mysql_client_manager.session_factory() as meta_session, dw_mysql_client_manager.session_factory() as dw_session):
            context = DataAgentContext(
                embedding_client=embedding_client_manager.client,
                column_qdrant_repository=ColumnQdrantRepository(qdrant_client_manager.client),
                metric_qdrant_repository=MetricQdrantRepository(qdrant_client_manager.client),
                value_es_repository=ValueESRepository(es_client_manager.client),
                meta_mysql_repository=MetaMySQLRepository(meta_session),
                dw_mysql_repository=DWMySQLRepository(dw_session)
            )
            # 调用图流式输出
            async for chunk in graph.astream(input = state, context=context,
                                             stream_mode="custom"):
                print(chunk)
        # 关闭客户端
        await qdrant_client_manager.close()
        await es_client_manager.close()
        await dw_mysql_client_manager.close()
        await meta_mysql_client_manager.close()
    asyncio.run(test_graph())