"""
  @Author:LiShuo
  @Time:2026/10/8
  @Desc:
"""
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.entities.column_info import ColumnInfo
from app.entities.column_metric import ColumnMetric
from app.entities.metric_info import MetricInfo
from app.entities.table_info import TableInfo
from app.mappers.column_info_mapper import ColumnInfoMapper
from app.mappers.column_metric_mapper import ColumnMetricMapper
from app.mappers.metric_info_mapper import MetricInfoMapper
from app.mappers.table_info_mapper import TableInfoMapper
from app.models.column_info_mysql import ColumnInfoMySQL
from app.models.column_metric_mysql import ColumnMetricMySQL
from app.models.metric_info_mysql import MetricInfoMySQL
from app.models.table_info_mysql import TableInfoMySQL


class MetaMySQLRepository:
    """跟MySQL数据库（元数据库）交互持久层 必须通过Session对象进行CURD"""
    def __init__(self,session:AsyncSession):
        self.session = session

    async def clear_all(self):
        """清空元数据库4张表，保证构建脚本可重复执行"""
        # 必须在本方法内提交事务：否则会与后续 save 方法里的 session.begin() 冲突
        # 用 commit() 而非 session.begin()：前者在 session 已自动开启事务时同样可用
        for model in (ColumnMetricMySQL, ColumnInfoMySQL, MetricInfoMySQL, TableInfoMySQL):
            await self.session.execute(delete(model))
        await self.session.commit()

    async def save_table_infos(self, table_infos: list[TableInfo]):
        """批量保存表信息"""
        # 将业务实体对象TableInfo 转为 数据库ORM实体TableInfoMySQL
        models = [TableInfoMapper.to_model(table_info) for table_info in table_infos]
        self.session.add_all(models)

    async def save_column_infos(self, column_infos: list[ColumnInfo]):
        """批量保存字段信息"""
        models = [ColumnInfoMapper.to_model(column_info) for column_info in column_infos]
        self.session.add_all(models)

    async def save_metric_info_to_meta_db(self, metric_infos: list[MetricInfo]):
        models = [MetricInfoMapper.to_model(metric_info) for metric_info in metric_infos]
        self.session.add_all(models)

    async def save_column_metric_info_to_meta_db(self, column_metrics: list[ColumnMetric]):
        models = [ColumnMetricMapper.to_model(column_metric) for column_metric in column_metrics]
        self.session.add_all(models)

