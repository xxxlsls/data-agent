"""
  @Author:LiShuo
  @Time:2026/10/8
  @Desc:知识库构建脚本入口
"""


import argparse
import asyncio
from pathlib import Path

from app.clients.embedding_client_manager import embedding_client_manager
from app.clients.es_client_manager import es_client_manager
from app.clients.mysql_client_manager import dw_mysql_client_manager, meta_mysql_client_manager
from app.clients.qdrant_client_manager import qdrant_client_manager
from app.core.log import logger
from app.repositories.es.value_es_repository import ValueESRepository
from app.repositories.mysql.dw.dw_mysql_repository import DWMySQLRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMySQLRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository
from app.services.meta_knowledge_service import MetaKnowledgeService


async def build(config_path: Path):
    """
    构建元知识库函数
    执行构建元知识库相关的业务逻辑

    """
    logger.info("正在构建元数据库...")

    # 1.初始化工作
    #1.1 对dw数据库管理器进行初始化,获取session_factory
    dw_mysql_client_manager.init()
    #1.2对meta数据库管理器对象进行初始化 得到 session_factory
    meta_mysql_client_manager.init()
    # 1.3 对qdrant客户端初始化
    qdrant_client_manager.init()
    embedding_client_manager.init()
    # 1.4 对ES客户端初始化
    es_client_manager.init()

    # 2.通过mysql客户端管理器获得session对象操作不同库
    async with (
        dw_mysql_client_manager.session_factory() as dw_session,
        meta_mysql_client_manager.session_factory() as meta_session,
    ):
        # 3. 创建业务层对象
        meta_knowledge_service = MetaKnowledgeService(
            meta_mysql_repository=MetaMySQLRepository(meta_session),
            dw_mysql_repository=DWMySQLRepository(dw_session),
            column_qdrant_repository=ColumnQdrantRepository(qdrant_client_manager.client),
            embedding_client=embedding_client_manager.client,
            value_es_repository=ValueESRepository(es_client_manager.client),
            metric_qdrant_repository=MetricQdrantRepository(qdrant_client_manager.client)
        )
        # 4. 调用业务对象 build 函数 完成元数据知识库的构建
        await meta_knowledge_service.build(config_path)

        # 5. 关闭连接（数据库、ES、Qdrant）
        await dw_mysql_client_manager.close()
        await meta_mysql_client_manager.close()
        await qdrant_client_manager.close()
        await es_client_manager.close()



if __name__ == "__main__":
    #创建一个命令行参数解析器对象
    parser = argparse.ArgumentParser(
        prog='python -m app.scripts.build_meta_knowledge',
        description='通过脚本+额外脚本(-c 传递)参数实现',
        epilog='========结束=========='
    )
    # 添加一个参数，支持短选项 -c 和长选项--conf
    # 该选项用于接收配置文件的路径
    parser.add_argument('-c','--conf', required=True)
    # 解析命令行传入的所有参数，并将结果存入 args 对象
    args = parser.parse_args()
    # 获取到脚本参数中 - yaml文件路径
    config_path:Path = Path(args.conf)

    # 2.执行构建元数据知识库
    asyncio.run(build(config_path))