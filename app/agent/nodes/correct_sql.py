"""
  @Author:LiShuo
  @Time:2026/10/9
  @Desc:负责定义校正SQL的节点
"""
from langgraph.config import get_stream_writer
from langgraph.runtime import Runtime
from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.core.log import logger


async def correct_sql(state:DataAgentState,runtime:Runtime[DataAgentContext]):
        writer = get_stream_writer()
        try:
                writer({"type": "progress", "step": "校正SQL", "status": "running"})
                # TODO 业务逻辑
                writer({"type": "progress", "step": "校正SQL", "status": "success"})
                # 校正次数自增,用于限制回环轮数
                return {"error": None, "correct_count": state.get("correct_count", 0) + 1}
        except Exception as e:
                logger.error(str(e))
                writer({"type": "progress", "step": "校正SQL", "status": "error"})
                return {"error": str(e), "correct_count": state.get("correct_count", 0) + 1}
