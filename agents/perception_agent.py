"""感知 Agent - 负责获取数据源"""
import imaplib
import email
from email.header import decode_header
from pathlib import Path
from typing import List

from config import settings
from agents.base_agent import BaseAgent
from utils.file_handler import FileHandler


class PerceptionAgent(BaseAgent):
    """感知 Agent：从邮件和文件夹获取待处理文件"""
    
    def __init__(self):
        super().__init__("PerceptionAgent")
        self.file_handler = FileHandler()
    
    def fetch_from_email(self) -> List[Path]:
        """从邮箱下载附件"""
        downloaded = []
        
        try:
            mail = imaplib.IMAP4_SSL(settings.MAIL_HOST)
            mail.login(settings.MAIL_USER, settings.MAIL_PASS)
            mail.select("INBOX")
            
            # 搜索未读邮件
            status, messages = mail.search(None, "UNSEEN")
            if status != "OK":
                return downloaded
            
            for num in messages[0].split():
                status, msg_data = mail.fetch(num, "(RFC822)")
                if status != "OK":
                    continue
                
                msg = email.message_from_bytes(msg_data[0][1])
                subject = decode_header(msg.get("Subject", ""))[0][0]
                if isinstance(subject, bytes):
                    subject = subject.decode()
                self.log(f"处理邮件: {subject[:50]}")
                
                # 提取 Excel 附件
                for part in msg.walk():
                    if part.get_content_disposition() == "attachment":
                        filename = part.get_filename()
                        if filename and (filename.endswith(".xlsx") or filename.endswith(".xls")):
                            filepath = settings.WATCH_FOLDER / filename
                            with open(filepath, "wb") as f:
                                f.write(part.get_payload(decode=True))
                            downloaded.append(filepath)
                            self.log(f"下载附件: {filename}")
            
            mail.close()
            mail.logout()
            
        except Exception as e:
            self.log_error(f"邮件获取失败: {e}")
        
        return downloaded
    
    def fetch_from_local(self) -> List[Path]:
        """扫描本地文件夹"""
        return self.file_handler.get_pending_files()
    
    def run(self, **kwargs) -> dict:
        """获取所有待处理文件"""
        use_email = kwargs.get('use_email', True)
        
        all_files = []
        
        if use_email:
            email_files = self.fetch_from_email()
            all_files.extend(email_files)
        
        local_files = self.fetch_from_local()
        all_files.extend(local_files)
        
        # 去重
        all_files = list(set(all_files))
        
        result = {
            "status": "success",
            "files": all_files,
            "count": len(all_files)
        }
        
        self.log(f"共获取 {len(all_files)} 个文件")
        return result