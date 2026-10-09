"""
  @Author:LiShuo
  @Time:2026/9/30
  @Desc:所有orm模型的基类
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """所有ORM模型父类，可以定义一些公共属性"""
    pass