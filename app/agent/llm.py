"""
  @Author:LiShuo
  @Time:2026/10/9
  @Desc:
"""

from langchain.chat_models import init_chat_model

from app.conf.app_config import app_config

llm = init_chat_model(
    model=app_config.llm.model_name,
    api_key = app_config.llm.api_key,
    base_url = app_config.llm.base_url,
    temperature = 0,
    model_provider='openai'

)

if __name__ == '__main__':
    #测试
    result = llm.invoke('给我说说人工智能的发展历史')
    print(result)