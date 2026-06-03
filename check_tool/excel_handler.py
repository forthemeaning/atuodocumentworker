import pandas as pd
from typing import List, Dict, Any, Optional
import os

class ExcelHandler:
    """Excel文件处理器"""
    
    @staticmethod
    def read_excel(file_path: str) -> Optional[pd.DataFrame]:
        """
        读取Excel文件
        
        Args:
            file_path: Excel文件路径
        
        Returns:
            DataFrame: 读取的数据，失败返回None
        """
        try:
            df = pd.read_excel(file_path)
            print(f"读取到 {len(df)} 条配置")
            return df
        except Exception as e:
            print(f"读取Excel失败: {e}")
            return None
    
    @staticmethod
    def write_excel(data: List[Dict[str, Any]], file_path: str, columns: List[str] = []) -> bool:
        """
        写入Excel文件
        
        Args:
            data: 数据列表
            file_path: 输出文件路径
            columns: 列名顺序
        
        Returns:
            bool: 是否成功
        """
        try:
            if not data:
                data = [{'结果': '无匹配内容'}]
            df = pd.DataFrame(data)
            if columns:
                df = df[columns]
            df.to_excel(file_path, index=False)
            return True
        except Exception as e:
            print(f"写入Excel失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    @staticmethod
    def filter_valid_rows(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """
        过滤有效行（指定列中至少有一个不为空）
        
        Args:
            df: 数据框
            columns: 列名列表
        
        Returns:
            DataFrame: 过滤后的数据框
        """
        mask = pd.Series(False, index=df.index)
        
        for col in columns:
            if col in df.columns:
                mask |= (df[col].notna() & (df[col] != ''))
        
        return df[mask]