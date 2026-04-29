"""文件处理工具"""
import shutil
from pathlib import Path
from typing import List, Optional
import pandas as pd

from config.settings import WATCH_FOLDER, PROCESSED_FOLDER, ERROR_FOLDER
from utils.logger import logger


class FileHandler:
    """文件处理器"""
    
    @staticmethod
    def get_pending_files() -> List[Path]:
        """获取所有待处理的 Excel 文件"""
        files = []
        for ext in ["*.xlsx", "*.xls"]:
            files.extend(WATCH_FOLDER.glob(ext))
        logger.info(f"发现 {len(files)} 个待处理文件")
        return files
    
    @staticmethod
    def read_excel(filepath: Path) -> Optional[pd.DataFrame]:
        """读取 Excel 文件"""
        try:
            df = pd.read_excel(filepath)
            logger.info(f"读取成功: {filepath.name}, {len(df)} 行, {list(df.columns)}")
            return df
        except Exception as e:
            logger.error(f"读取失败 {filepath.name}: {e}")
            return None
    
    @staticmethod
    def archive_file(filepath: Path, status: str = "success"):
        """归档文件"""
        target = PROCESSED_FOLDER if status == "success" else ERROR_FOLDER
        dest = target / filepath.name
        
        # 如果目标已存在，添加时间戳
        if dest.exists():
            timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
            dest = target / f"{filepath.stem}_{timestamp}{filepath.suffix}"
        
        shutil.move(str(filepath), str(dest))
        logger.info(f"文件已归档: {dest}")
    
    @staticmethod
    def save_error_log(filepath: Path, error_msg: str):
        """保存错误信息"""
        error_file = ERROR_FOLDER / f"{filepath.stem}_error.txt"
        with open(error_file, "w", encoding="utf-8") as f:
            f.write(f"文件: {filepath.name}\n")
            f.write(f"时间: {pd.Timestamp.now()}\n")
            f.write(f"错误: {error_msg}\n")