"""
  @Author:LiShuo
  @Time:2026/10/12
  @Desc:负责定义查询接口
"""
import asyncio
from typing import Annotated

from fastapi import APIRouter, Depends


from starlette.responses import StreamingResponse

from app.api.dependencies import get_query_service
from app.api.schemas.query_schema import QuerySchema
from app.services.query_service import QueryService

# 声明查询的路由
query_router = APIRouter()


# async def fake_video_streamer():
#     """
#     模拟生成器函数
#     :return:
#     """
#     for i in range(10):
#         # 添加睡眠，演示延时效果
#         await asyncio.sleep(1)
#         yield f'data: {{"stage": {i}}}\n\n'

@query_router.post("/api/query")

# 定义POST接口/api/query
@query_router.post("/api/query")
async def query(query: QuerySchema, query_service:QueryService = Depends(get_query_service)):
    """
     前后端约定提交参数 采用请求体：{"query":"统计各分类销售商品数量"}
    :param query: 问题
    :return: 异步流式返回
        进度展示 约定{type:"progress",step:"召回字段","status":"running"}
        数据展示 约定{type:"result","data":业务数据}
        sse协议：data: 数据 \n\n
    """
    return StreamingResponse(query_service.query_answer(query.query), media_type="text/event-stream")