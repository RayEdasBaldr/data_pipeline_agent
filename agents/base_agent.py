"""Agent 基类"""
from abc import ABC, abstractmethod
from typing import Any, Dict

from utils.logger import logger


class BaseAgent(ABC):
    """所有 Agent 的抽象基类"""
    
    def __init__(self, name: str):
        self.name = name
        logger.info(f"初始化 Agent: {name}")
    
    @abstractmethod
    def run(self, **kwargs) -> Dict[str, Any]:
        """执行 Agent 任务，返回结果字典"""
        pass
    
    def log(self, msg: str):
        """带 Agent 名称的日志"""
        logger.info(f"[{self.name}] {msg}")
    
    def log_error(self, msg: str):
        logger.error(f"[{self.name}] {msg}")
