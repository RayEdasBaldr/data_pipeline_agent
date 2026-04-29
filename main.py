"""程序入口"""
import sys
import argparse
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from orchestrator.pipeline import DataPipelineOrchestrator
from utils.logger import logger


def main():
    parser = argparse.ArgumentParser(description="数据搬运 Agent")
    parser.add_argument(
        "--mode", 
        choices=["once", "forever"],
        default="once",
        help="运行模式: once(单次) / forever(持续)"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="持续模式下的检查间隔(秒)"
    )
    parser.add_argument(
        "--instruction",
        type=str,
        default=None,
        help="自然语言指令，例如: '筛选金额大于10000的记录'"
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("数据搬运 Agent 启动")
    logger.info(f"模式: {args.mode}")
    if args.instruction:
        logger.info(f"指令: {args.instruction}")
    logger.info("=" * 60)
    
    orchestrator = DataPipelineOrchestrator()
    
    if args.mode == "once":
        results = orchestrator.run_once(instruction=args.instruction)
        logger.info("执行完成")
    else:
        orchestrator.run_forever(interval_seconds=args.interval)


if __name__ == "__main__":
    main()