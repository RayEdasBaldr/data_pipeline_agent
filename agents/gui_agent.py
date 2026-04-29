"""GUI 控制 Agent - 负责桌面软件自动化"""
import time
import subprocess
from typing import List, Dict
import pyautogui
import pygetwindow as gw

from config import settings
from agents.base_agent import BaseAgent
from utils.clipboard_helper import ClipboardHelper


class GUIControlAgent(BaseAgent):
    """GUI 控制 Agent：模拟键盘鼠标操作桌面软件"""
    
    def __init__(self):
        super().__init__("GUIControlAgent")
        self.clipboard = ClipboardHelper()
        self.window = None
        
        # 安全设置
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.2
    
    def activate_window(self, title: str) -> bool:
        """激活目标窗口"""
        try:
            windows = gw.getWindowsWithTitle(title)
            if windows:
                self.window = windows[0]
                
                # 如果窗口最小化，先恢复
                if self.window.isMinimized:
                    self.window.restore()
                
                self.window.activate()
                time.sleep(settings.INPUT_DELAY)
                self.log(f"激活窗口: {title}")
                return True
            
            # 尝试启动程序（示例：记事本）
            self.log(f"未找到窗口 {title}，尝试启动...")
            subprocess.Popen(["notepad.exe"])
            time.sleep(2)
            
            windows = gw.getWindowsWithTitle("记事本")
            if windows:
                self.window = windows[0]
                return True
                
        except Exception as e:
            self.log_error(f"激活窗口失败: {e}")
        
        return False
    
    def click_position(self, x: int, y: int, description: str = ""):
        """点击指定坐标"""
        pyautogui.click(x, y)
        time.sleep(0.3)
        if description:
            self.log(f"点击: {description} ({x}, {y})")
    
    def send_text(self, text: str):
        """发送文本（支持中文）"""
        self.clipboard.copy(text)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.2)
    
    def press_tab(self, times: int = 1):
        """按 Tab 键"""
        for _ in range(times):
            pyautogui.press('tab')
            time.sleep(0.1)
    
    def press_enter(self):
        """按回车键"""
        pyautogui.press('enter')
        time.sleep(0.3)
    
    def press_shortcut(self, *keys):
        """按快捷键"""
        pyautogui.hotkey(*keys)
        time.sleep(0.3)
    
    def fill_form(self, data_row: Dict, field_order: List[str]):
        """填写单条记录"""
        for i, field in enumerate(field_order):
            value = data_row.get(field, "")
            if value:
                self.send_text(str(value))
                self.log(f"  填入 [{field}]: {str(value)[:30]}")
            
            # 不是最后一个字段就 Tab
            if i < len(field_order) - 1:
                self.press_tab(1)
        
        self.press_enter()
    
    def fill_multiple_records(self, records: List[Dict], field_order: List[str]) -> int:
        """批量填写多条记录"""
        success_count = 0
        
        for idx, record in enumerate(records):
            self.log(f"录入第 {idx+1}/{len(records)} 条")
            try:
                self.fill_form(record, field_order)
                success_count += 1
                time.sleep(0.8)
            except Exception as e:
                self.log_error(f"录入失败: {e}")
        
        self.log(f"批量录入完成: {success_count}/{len(records)} 成功")
        return success_count
    
    def run(self, **kwargs) -> dict:
        """执行 GUI 录入"""
        records = kwargs.get("records", [])
        target_fields = kwargs.get("target_fields", [])
        target_app = kwargs.get("target_app", settings.TARGET_APP_TITLE)
        
        if not records:
            return {"status": "skipped", "reason": "无数据", "success": 0}
        
        if not self.activate_window(target_app):
            return {"status": "error", "reason": f"无法激活窗口 {target_app}"}
        
        # 可选：等待用户手动定位到起始位置
        time.sleep(1)
        
        success = self.fill_multiple_records(records, target_fields)
        
        return {
            "status": "success" if success > 0 else "partial",
            "total": len(records),
            "success": success
        }