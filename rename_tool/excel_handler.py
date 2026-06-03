import pandas as pd
from typing import List, Dict, Any, Optional


class ExcelHandler:
    """Excel文件处理类"""
    
    @staticmethod
    def read_excel(file_path: str) -> Optional[pd.DataFrame]:
        """
        读取Excel文件
        
        Args:
            file_path: Excel文件路径
        
        Returns:
            DataFrame or None: 读取的数据
        """
        try:
            return pd.read_excel(file_path)
        except Exception as e:
            print(f"读取Excel失败: {e}")
            return None
    
    @staticmethod
    def write_excel(data: List[Dict[str, Any]], file_path: str, index: bool = False) -> bool:
        """
        写入Excel文件
        
        Args:
            data: 数据列表
            file_path: 输出文件路径
            index: 是否包含索引
        
        Returns:
            bool: 是否成功
        """
        try:
            df = pd.DataFrame(data)
            df.to_excel(file_path, index=index)
            return True
        except Exception as e:
            print(f"写入Excel失败: {e}")
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
            elif col.startswith('子名'):  # 处理动态子名字段
                # 如果指定了子名字段，但表格中不存在，不添加到mask中
                continue
        
        return df[mask]