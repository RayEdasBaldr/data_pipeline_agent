"""规划 Agent - 负责任务拆解和 LLM 推理"""
import json
from typing import Dict, List, Any
import pandas as pd
from openai import OpenAI

from config import settings
from agents.base_agent import BaseAgent
from utils.logger import logger


class PlanningAgent(BaseAgent):
    """规划 Agent：使用 LLM 进行长链推理和任务拆解"""
    
    def __init__(self):
        super().__init__("PlanningAgent")
        self.client = OpenAI(
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL
        )
    
    def parse_instruction(self, instruction: str, df_columns: List[str]) -> Dict:
        """将自然语言指令解析为可执行计划"""
        
        prompt = f"""
你是一个任务规划专家。用户需要将 Excel 数据录入到桌面软件中。

用户指令：{instruction}

Excel 表格包含的列：{df_columns}

请将指令拆解为以下 JSON 格式：
{{
    "filters": [
        {{"column": "列名", "operator": "操作符", "value": 比较值}}
    ],
    "target_fields": ["需要提取的列名1", "列名2"],
    "target_app": "目标软件名称",
    "field_mapping": {{
        "Excel列名": "软件输入框名称"
    }}
}}

操作符支持：> , < , = , contains

示例：
指令："筛选金额大于10000且状态为已回款的记录，提取客户名称和金额"
输出：
{{
    "filters": [
        {{"column": "金额", "operator": ">", "value": 10000}},
        {{"column": "状态", "operator": "=", "value": "已回款"}}
    ],
    "target_fields": ["客户名称", "金额"],
    "target_app": "ERP系统",
    "field_mapping": {{}}
}}

请只输出 JSON，不要有其他内容：
"""
        
        try:
            response = self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            # 提取 JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            plan = json.loads(content)
            self.log(f"规划完成: filters={len(plan.get('filters', []))}")
            return plan
            
        except Exception as e:
            self.log_error(f"LLM 规划失败: {e}")
            # 返回默认计划
            return {
                "filters": [],
                "target_fields": df_columns[:3] if df_columns else [],
                "target_app": settings.TARGET_APP_TITLE,
                "field_mapping": {}
            }
    
    def apply_filters(self, df: pd.DataFrame, filters: List[Dict]) -> pd.DataFrame:
        """应用筛选条件"""
        for f in filters:
            col = f.get("column")
            op = f.get("operator")
            val = f.get("value")
            
            if not col or col not in df.columns:
                continue
            
            try:
                if op == ">":
                    df = df[df[col].astype(float) > float(val)]
                elif op == "<":
                    df = df[df[col].astype(float) < float(val)]
                elif op == "=":
                    df = df[df[col].astype(str) == str(val)]
                elif op == "contains":
                    df = df[df[col].astype(str).str.contains(str(val), na=False)]
                self.log(f"应用筛选: {col} {op} {val} → 剩余 {len(df)} 行")
            except Exception as e:
                self.log_error(f"筛选失败 {col} {op} {val}: {e}")
        
        return df
    
    def run(self, **kwargs) -> dict:
        """执行规划任务"""
        df = kwargs.get("df")
        instruction = kwargs.get("instruction", "录入所有数据")
        
        if df is None:
            return {"status": "error", "reason": "缺少 DataFrame"}
        
        columns = list(df.columns)
        plan = self.parse_instruction(instruction, columns)
        
        # 应用筛选
        filtered_df = self.apply_filters(df, plan.get("filters", []))
        
        # 提取目标字段
        target_fields = plan.get("target_fields", columns[:3])
        available_fields = [f for f in target_fields if f in filtered_df.columns]
        
        records = filtered_df[available_fields].to_dict('records')
        
        result = {
            "status": "success",
            "plan": plan,
            "original_rows": len(df),
            "filtered_rows": len(filtered_df),
            "target_fields": available_fields,
            "records": records
        }
        
        self.log(f"原始 {len(df)} 行 → 筛选后 {len(filtered_df)} 行 → {len(records)} 条记录")
        return result