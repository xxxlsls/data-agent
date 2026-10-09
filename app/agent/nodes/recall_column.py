"""
  @Author:LiShuo
  @Time:2026/10/9
  @Desc:负责定义召回字段信息的节点
"""
import keyword

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.config import get_stream_writer
from langgraph.runtime import Runtime
from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from app.clients.embedding_client_manager import embedding_client_manager
from app.core.log import logger
from app.entities.column_info import ColumnInfo
from prompt.prompt_loader import load_prompt


async def recall_column(state:DataAgentState,runtime:Runtime[DataAgentContext]):
        writer = get_stream_writer()
        try:
                writer({"type": "progress", "step": "召回字段信息", "status": "running"})

                # 1.调用大模型完成keywords列表的问题进行增强  扩展关键词
                query = state["query"]

                #1.1加载提示词
                prompt = PromptTemplate(
                        template=load_prompt('extend_keywords_for_column_recall'),
                        input_variables=[query]
                )

                #1.2 定义JSON解析器对象 通过"管道符"|组合运行多个运行单元
                parser = JsonOutputParser()
                chain = prompt | llm | parser
                result = await chain.ainvoke({"query": query})

                # 2.关键词列表：抽取关键词+扩展后
                logger.info(f'对关键词扩展后的字段列表:{result}')
                keywords = state["keywords"]
                keywords = list(set(keywords + result))

                # 3.遍历关键词列表，根据关键词查询qdrant进行语义相近检索
                retrieved_column_map: dict[str, ColumnInfo] = {}
                embedding_client = runtime.context["embedding_client"]
                column_qdrant_repository = runtime.context["column_qdrant_repository"]

                embedding = await embedding_client.aembed_query(keyword)
                column_infos: list[ColumnInfo] = await column_qdrant_repository.search(embedding)
                #对
                for column_info in column_infos:
                        column_id = column_info.id
                        if column_id not in retrieved_column_map:
                                retrieved_column_map[column_id] = column_info


                writer({"type": "progress", "step": "召回字段信息", "status": "success"})
        except Exception as e:
                logger.error(f"召回字段失败, 错误信息: {str(e)}")
                writer({"type": "progress", "step": "召回字段信息", "status": "error"})
                raise
