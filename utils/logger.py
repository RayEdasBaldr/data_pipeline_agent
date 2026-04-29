"""日志工具"""
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

from config.settings import LOGS_DIR


class Logger:
    _instance: Optional['Logger'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.log_file = LOGS_DIR / f"agent_{datetime.now().strftime('%Y%m%d')}.log"
    
    def _write(self, level: str, msg: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        log_line = f"[{timestamp}] [{level}] {msg}"
        print(log_line, file=sys.stdout)
        
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_line + "\n")
        except Exception:
            pass
    
    def info(self, msg: str):
        self._write("INFO", msg)
    
    def warning(self, msg: str):
        self._write("WARNING", msg)
    
    def error(self, msg: str):
        self._write("ERROR", msg)
    
    def debug(self, msg: str):
        self._write("DEBUG", msg)


# 全局日志实例
logger = Logger()
