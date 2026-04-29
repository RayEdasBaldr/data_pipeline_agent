"""配置文件"""
import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent.parent

# 邮件配置
MAIL_HOST = "imap.163.com"
MAIL_USER = "your_email@163.com"
MAIL_PASS = "your_authorization_code"

# 文件目录配置
DATA_DIR = BASE_DIR / "data"
WATCH_FOLDER = DATA_DIR / "incoming"
PROCESSED_FOLDER = DATA_DIR / "processed"
ERROR_FOLDER = DATA_DIR / "error"
LOGS_DIR = BASE_DIR / "logs"

# LLM 配置
LLM_API_KEY = "your-api-key"
LLM_BASE_URL = "https://api.openai.com/v1"
LLM_MODEL = "gpt-4o-mini"

# GUI 控制配置
TARGET_APP_TITLE = "记事本"  # 可替换为"金蝶"、"用友"等
INPUT_DELAY = 0.5  # 操作间隔（秒）

# 运行配置
POLL_INTERVAL = 60  # 轮询间隔（秒）

# 创建必要目录
for dir_path in [WATCH_FOLDER, PROCESSED_FOLDER, ERROR_FOLDER, LOGS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)
