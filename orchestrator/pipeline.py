"""主控流程 - 协调所有 Agent"""
from typing import Dict, Optional
from pathlib import Path

from agents.perception_agent import PerceptionAgent
from agents.planning_agent import PlanningAgent
from agents.gui_agent import GUIControlAgent
from agents.verification_agent import VerificationAgent
from utils.file_handler import FileHandler
from utils.logger import logger


class DataPipelineOrchestrator:
    """数据搬运主控器"""
    
    def __init__(self):
        self.perception = PerceptionAgent()
        self.planner = PlanningAgent()
        self.gui = GUIControlAgent()
        self.verifier = VerificationAgent()
        self.file_handler = FileHandler()
    
    def process_file(self, filepath: Path, instruction: str = None) -> Dict:
        """处理单个文件"""
        logger.info(f"=" * 50)
        logger.info(f"开始处理: {filepath.name}")
        
        result = {
            "file": str(filepath),
            "status": "unknown",
            "details": {}
        }
        
        try:
            # 1. 读取 Excel
            df = self.file_handler.read_excel(filepath)
            if df is None:
                result["status"] = "error"
                result["reason"] = "读取失败"
                self.file_handler.archive_file(filepath, "error")
                return result
            
            # 2. 规划任务（LLM 推理）
            plan_result = self.planner.run(df=df, instruction=instruction)
            if plan_result["status"] != "success":
                result["status"] = "error"
                result["reason"] = "规划失败"
                return result
            
            records = plan_result["records"]
            target_fields = plan_result["target_fields"]
            
            if not records:
                logger.info("无数据需要录入，跳过")
                result["status"] = "skipped"
                result["reason"] = "无数据"
                return result
            
            # 3. GUI 录入
            gui_result = self.gui.run(
                records=records,
                target_fields=target_fields,
                target_app=plan_result["plan"].get("target_app")
            )
            result["details"]["gui"] = gui_result
            
            # 4. 验证
            verify_result = self.verifier.run(
                expected_count=len(records),
                actual_count=gui_result.get("success", 0),
                window_title=plan_result["plan"].get("target_app", "")
            )
            result["details"]["verification"] = verify_result
            
            # 5. 判断最终状态
            if verify_result["status"] == "passed":
                result["status"] = "success"
            elif gui_result.get("success", 0) > 0:
                result["status"] = "partial"
            else:
                result["status"] = "failed"
            
            # 6. 归档
            if result["status"] in ["success", "skipped"]:
                self.file_handler.archive_file(filepath, "success")
            else:
                self.file_handler.archive_file(filepath, "error")
                
        except Exception as e:
            logger.error(f"处理失败: {e}")
            result["status"] = "error"
            result["reason"] = str(e)
            self.file_handler.archive_file(filepath, "error")
        
        logger.info(f"处理结果: {result['status']}")
        return result
    
    def run_once(self, instruction: str = None):
        """单次执行"""
        logger.info("开始执行数据搬运任务")
        
        # 获取待处理文件
        perception_result = self.perception.run()
        files = perception_result.get("files", [])
        
        if not files:
            logger.info("没有待处理文件")
            return
        
        results = []
        for filepath in files:
            result = self.process_file(filepath, instruction)
            results.append(result)
        
        # 汇总统计
        success_count = sum(1 for r in results if r["status"] == "success")
        logger.info(f"任务完成: 成功 {success_count}/{len(results)}")
        
        return results
    
    def run_forever(self, interval_seconds: int = 60):
        """持续运行模式"""
        logger.info(f"启动持续运行模式，间隔 {interval_seconds} 秒")
        
        import time
        while True:
            try:
                self.run_once()
                time.sleep(interval_seconds)
            except KeyboardInterrupt:
                logger.info("收到停止信号，退出...")
                break
            except Exception as e:
                logger.error(f"运行异常: {e}")
                time.sleep(interval_seconds)
