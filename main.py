"""
  @Author:LiShuo
  @Time:2026/10/12
  @Desc:FastApi入口脚本
"""
import asyncio
import time
import uuid
from urllib.request import Request

from fastapi import FastAPI
from starlette.responses import StreamingResponse

from app.api.routers.query_router import query_router, fake_video_streamer
from app.core import lifespan
from app.core.context import request_id_ctx_var

# 创建fastapi入口实例
app = FastAPI(lifespan=lifespan)

# @app.middleware("http")
# async def add_process_time_header(request: Request, call_next):
#     # 记录请求处理开始时间（使用高精度计时器）
#     start_time = time.perf_counter()
#     # 调用后续的请求处理逻辑（路由函数/其他中间件），获取响应对象
#     response = await call_next(request)
#     # 计算请求处理总耗时（结束时间 - 开始时间）
#     process_time = time.perf_counter() - start_time
#     # 将处理耗时添加到响应头中，键为X-Process-Time，值为耗时字符串
#     response.headers["X-Process-Time"] = str(process_time)
#     # 返回处理后的响应对象
#     return response


# 添加中间件，在每个请求中生成唯一的request_id
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    # 调用路径函数之前
    request_id_ctx_var.set(uuid.uuid4())
    # 调用路径函数
    response = await call_next(request)
    # 调用路径函数之后
    return response

# 绑定查询的路由
app.include_router(query_router)
# # 模拟视频流生成器函数（异步）
# async def fake_video_streamer():
#     # 循环生成10次模拟视频字节数据
#     for i in range(10):
#         # 添加睡眠，演示延时效果
#         await asyncio.sleep(1)
#         yield f'data: {{"stage": {i}}}\n\n'

# 定义根路径GET接口
@app.get("/")
async def main():
    # 返回流式响应，传入视频流生成器
    return StreamingResponse(fake_video_streamer())