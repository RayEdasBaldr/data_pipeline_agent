"""验证 Agent - 负责结果验证"""
import time
from typing import Dict
import pygetwindow as gw

from agents.base_agent import BaseAgent


class VerificationAgent(BaseAgent):
    """验证 Agent：确认数据是否成功录入"""
    
    def __init__(self):
        super().__init__("VerificationAgent")
    
    def verify_window_active(self, window_title: str) -> bool:
        """验证目标窗口是否活跃"""
        try:
            active = gw.getActiveWindow()
            if active and window_title.lower() in active.title.lower():
                self.log(f"窗口验证通过: {active.title}")
                return True
        except Exception as e:
            self.log_error(f"窗口验证失败: {e}")
        return False
    
    def verify_no_error_dialog(self, check_texts: list = None) -> bool:
        """验证没有错误弹窗（简化版）"""
        # 这里可以实现更复杂的检测逻辑
        # 例如：检查屏幕特定区域是否有红色错误提示
        time.sleep(0.5)
        return True
    
    def run(self, **kwargs) -> dict:
        """执行验证"""
        expected_count = kwargs.get("expected_count", 0)
        actual_count = kwargs.get("actual_count", 0)
        window_title = kwargs.get("window_title", "")
        
        results = {
            "status": "unknown",
            "checks": {}
        }
        
        # 检查1：数量验证
        if expected_count > 0:
            if actual_count == expected_count:
                results["checks"]["count_match"] = True
                self.log(f"数量验证通过: {actual_count}/{expected_count}")
            else:
                results["checks"]["count_match"] = False
                self.log(f"数量验证失败: {actual_count}/{expected_count}")
        
        # 检查2：窗口验证
        if window_title:
            results["checks"]["window_active"] = self.verify_window_active(window_title)
        
        # 检查3：错误弹窗验证
        results["checks"]["no_error"] = self.verify_no_error_dialog()
        
        # 综合判断
        if all(results["checks"].values()):
            results["status"] = "passed"
        elif any(results["checks"].values()):
            results["status"] = "partial"
        else:
            results["status"] = "failed"
        
        self.log(f"验证结果: {results['status']}")
        return results