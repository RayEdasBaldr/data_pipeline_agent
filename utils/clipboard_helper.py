"""剪贴板辅助工具"""
import time
try:
    import win32clipboard as clipboard
    import win32con
    WINDOWS = True
except ImportError:
    WINDOWS = False
    import pyperclip


class ClipboardHelper:
    """剪贴板操作封装，跨平台支持"""
    
    @staticmethod
    def copy(text: str):
        """复制文本到剪贴板"""
        if WINDOWS:
            clipboard.OpenClipboard()
            clipboard.EmptyClipboard()
            clipboard.SetClipboardText(str(text), win32con.CF_UNICODETEXT)
            clipboard.CloseClipboard()
        else:
            pyperclip.copy(str(text))
    
    @staticmethod
    def paste() -> str:
        """从剪贴板粘贴文本"""
        if WINDOWS:
            clipboard.OpenClipboard()
            text = clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
            clipboard.CloseClipboard()
            return text
        else:
            return pyperclip.paste()