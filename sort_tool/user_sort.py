"""
排序工具 - 用户脚本
用于快速调用排序功能，只需修改路径即可使用
"""

import os
import sys
from pathlib import Path

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from excel_handler import ExcelHandler
from sort_logic import SortLogic

def main():
    print("=" * 60)
    print("排序工具 - 用户脚本")
    print("=" * 60)
    
    # === 用户需要修改的部分 ===
    reference_file = r""
    target_file = r""
    # ========================
    
    if not reference_file:
        print("错误: 请先设置参照文件路径 (reference_file)")
        print("请修改脚本中的 reference_file 变量")
        return
    
    if not target_file:
        print("错误: 请先设置目标文件路径 (target_file)")
        print("请修改脚本中的 target_file 变量")
        return
    
    if not os.path.exists(reference_file):
        print(f"错误: 参照文件不存在 - {reference_file}")
        return
    
    if not os.path.exists(target_file):
        print(f"错误: 目标文件不存在 - {target_file}")
        return
    
    ref_columns = ExcelHandler.get_columns(reference_file)
    target_columns = ExcelHandler.get_columns(target_file)
    
    if not ref_columns or not target_columns:
        print("无法读取文件列名")
        return
    
    print(f"参照文件: {reference_file}")
    print(f"参照文件列: {ref_columns}")
    ref_col_idx = int(input(f"选择参照列 (1-{len(ref_columns)}): ").strip()) - 1
    ref_column = ref_columns[ref_col_idx]
    
    print(f"\n目标文件: {target_file}")
    print(f"目标文件列: {target_columns}")
    match_col_idx = int(input(f"选择匹配列 (1-{len(target_columns)}): ").strip()) - 1
    match_column = target_columns[match_col_idx]
    
    fuzzy = input("使用模糊匹配? (y/n, 默认n): ").strip().lower() == 'y'
    keep_unmatched = input("保留未匹配行? (y/n, 默认y): ").strip().lower() != 'n'
    
    print("\n正在排序...")
    ref_df = ExcelHandler.read_excel(reference_file)
    target_df = ExcelHandler.read_excel(target_file)
    ref_values = ExcelHandler.get_column_values(ref_df, ref_column)
    
    if fuzzy:
        sorted_df = SortLogic.fuzzy_sort_by_reference(target_df, ref_values, match_column, keep_unmatched)
    else:
        sorted_df = SortLogic.sort_by_reference(target_df, ref_values, match_column, keep_unmatched)
    
    output_path = target_file.replace('.xlsx', '_sorted.xlsx')
    ExcelHandler.write_excel(sorted_df, output_path)
    
    print(f"\n✅ 排序完成! 输出: {output_path}")

if __name__ == "__main__":
    main()