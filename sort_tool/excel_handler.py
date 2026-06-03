import pandas as pd
from typing import Optional, List
import os

class ExcelHandler:
    """Excel文件处理器"""
    
    @staticmethod
    def read_excel(file_path: str, sheet_name: int = 0) -> Optional[pd.DataFrame]:
        """读取Excel文件"""
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            return df
        except Exception as e:
            print(f"读取Excel失败: {e}")
            return None
    
    @staticmethod
    def write_excel(df: pd.DataFrame, file_path: str) -> bool:
        """写入Excel文件"""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            df.to_excel(file_path, index=False)
            return True
        except Exception as e:
            print(f"写入Excel失败: {e}")
            return False
    
    @staticmethod
    def get_columns(file_path: str) -> Optional[List[str]]:
        """获取Excel文件的所有列名"""
        try:
            df = pd.read_excel(file_path, nrows=0)
            return df.columns.tolist()
        except Exception as e:
            print(f"获取列名失败: {e}")
            return None
    
    @staticmethod
    def get_column_values(df: pd.DataFrame, column_name: str) -> List:
        """获取指定列的所有值"""
        if column_name not in df.columns:
            return []
        return df[column_name].dropna().tolist()