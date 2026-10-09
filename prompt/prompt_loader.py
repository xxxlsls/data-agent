"""
  @Author:LiShuo
  @Time:2026/10/9
  @Desc:负责定义提示词的加载逻辑
"""
from pathlib import Path

# 项目根目录（本文件位于 <root>/prompt/prompt_loader.py，故向上两级）
PROJECT_ROOT = Path(__file__).parents[1]

# 提示词模板所在目录。注意是复数 prompts，与当前文件所在的单数 prompt 目录区分开
PROMPTS_DIR = PROJECT_ROOT / "prompts"
