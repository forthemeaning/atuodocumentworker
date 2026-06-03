import pandas as pd
from typing import List, Optional

class SortLogic:
    """排序逻辑处理"""
    
    @staticmethod
    def sort_by_reference(
        target_df: pd.DataFrame, 
        reference_values: List, 
        match_column: str,
        keep_unmatched: bool = False
    ) -> pd.DataFrame:
        """
        根据参照值列表对目标DataFrame进行排序
        
        Args:
            target_df: 目标DataFrame（待排序的Excel数据）
            reference_values: 参照值列表（排序顺序依据）
            match_column: 匹配列名（用于与参照值匹配的列）
            keep_unmatched: 是否保留未匹配的行
        
        Returns:
            排序后的DataFrame
        """
        if match_column not in target_df.columns:
            print(f"错误: 列 '{match_column}' 不存在于目标文件中")
            return target_df
        
        result_list = []
        unmatched_list = []
        matched_indices = set()
        
        for ref_value in reference_values:
            matched_rows = target_df[target_df[match_column] == ref_value]
            for idx, row in matched_rows.iterrows():
                if idx not in matched_indices:
                    result_list.append(row)
                    matched_indices.add(idx)
        
        if keep_unmatched:
            for idx, row in target_df.iterrows():
                if idx not in matched_indices:
                    unmatched_list.append(row)
        
        if result_list:
            result_df = pd.DataFrame(result_list)
            if unmatched_list:
                unmatched_df = pd.DataFrame(unmatched_list)
                result_df = pd.concat([result_df, unmatched_df], ignore_index=True)
            return result_df
        elif unmatched_list:
            return pd.DataFrame(unmatched_list)
        
        return target_df
    
    @staticmethod
    def fuzzy_sort_by_reference(
        target_df: pd.DataFrame,
        reference_values: List,
        match_column: str,
        keep_unmatched: bool = False
    ) -> pd.DataFrame:
        """
        模糊匹配排序（将参照值转换为字符串后模糊匹配）
        """
        if match_column not in target_df.columns:
            print(f"错误: 列 '{match_column}' 不存在于目标文件中")
            return target_df
        
        target_df = target_df.copy()
        target_df['_temp_sort_key'] = target_df[match_column].astype(str)
        
        result_list = []
        unmatched_list = []
        matched_indices = set()
        
        for ref_value in reference_values:
            ref_str = str(ref_value)
            matched_rows = target_df[target_df['_temp_sort_key'].str.contains(ref_str, na=False)]
            for idx, row in matched_rows.iterrows():
                if idx not in matched_indices:
                    result_list.append(row)
                    matched_indices.add(idx)
        
        if keep_unmatched:
            for idx, row in target_df.iterrows():
                if idx not in matched_indices:
                    unmatched_list.append(row)
        
        if result_list:
            result_df = pd.DataFrame(result_list)
            result_df = result_df.drop(columns=['_temp_sort_key'])
            if unmatched_list:
                unmatched_df = pd.DataFrame(unmatched_list)
                unmatched_df = unmatched_df.drop(columns=['_temp_sort_key'])
                result_df = pd.concat([result_df, unmatched_df], ignore_index=True)
            return result_df
        elif unmatched_list:
            result_df = pd.DataFrame(unmatched_list)
            return result_df.drop(columns=['_temp_sort_key'])
        
        return target_df.drop(columns=['_temp_sort_key'])