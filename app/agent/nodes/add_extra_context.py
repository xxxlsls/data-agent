"""
  @Author:LiShuo
  @Time:2026/10/9
  @Desc:负责定义添加额外上下文信息的节点
"""
from langgraph.config import get_stream_writer
from langgraph.runtime import Runtime
from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.core.log import logger


async def add_extra_context(state:DataAgentState,runtime:Runtime[DataAgentContext]):
        writer = get_stream_writer()
        try:
                writer({"type": "progress", "step": "添加额外上下文信息", "status": "running"})
                # TODO 业务逻辑
                writer({"type": "progress", "step": "添加额外上下文信息", "status": "success"})
        except Exception as e:
                logger.error(str(e))
                writer({"type": "progress", "step": "添加额外上下文信息", "status": "error"})
                raise
