"""
排序工具 - 快速脚本
用于快速调用排序功能，只需修改路径即可使用
"""

import os
import sys
from pathlib import Path

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from excel_handler import ExcelHandler
from sort_logic import SortLogic

REFERENCE_FILE = r""
TARGET_FILE = r""

def main():
    print("快速排序脚本")
    
    if not REFERENCE_FILE:
        print("错误: 请设置 REFERENCE_FILE 变量")
        return
    
    if not TARGET_FILE:
        print("错误: 请设置 TARGET_FILE 变量")
        return
    
    ref_df = ExcelHandler.read_excel(REFERENCE_FILE)
    target_df = ExcelHandler.read_excel(TARGET_FILE)
    
    ref_columns = ref_df.columns.tolist()
    target_columns = target_df.columns.tolist()
    
    print(f"参照列: {ref_columns}")
    ref_col_idx = int(input(f"选择参照列 (1-{len(ref_columns)}): ").strip()) - 1
    ref_column = ref_columns[ref_col_idx]
    
    print(f"匹配列: {target_columns}")
    match_col_idx = int(input(f"选择匹配列 (1-{len(target_columns)}): ").strip()) - 1
    match_column = target_columns[match_col_idx]
    
    ref_values = ExcelHandler.get_column_values(ref_df, ref_column)
    sorted_df = SortLogic.sort_by_reference(target_df, ref_values, match_column, keep_unmatched=True)
    
    output_path = TARGET_FILE.replace('.xlsx', '_sorted.xlsx')
    ExcelHandler.write_excel(sorted_df, output_path)
    print(f"✅ 完成: {output_path}")

if __name__ == "__main__":
    main()