"""
  @Author:LiShuo
  @Time:2026/10/9
  @Desc:负责定义提示词的加载逻辑
"""
from pathlib import Path


def load_prompt(name: str) -> str:
    # 根据指定的名称拼接提示词所在的路径
    prompt_path = Path(__file__).parents[1] / "prompts" / f"{name}.prompt"
    # 可以使用Path中的函数直接读取即可
    return prompt_path.read_text(encoding="utf-8")