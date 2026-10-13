"""
  @Author:LiShuo
  @Time:2026/10/12
  @Desc:负责定义查询接口请求体结构
"""
from pydantic import BaseModel


# 定义查询请求的数据模型(用于接口入参校验)
class QuerySchema(BaseModel):
    query:str #接收用户输入的查询字符串,会自动校验字段类型和非空
