import sys
import os

from excel_handler import ExcelHandler
from sort_logic import SortLogic
from user_input import UserInput

def main():
    print("=" * 50)
    print("Excel 排序工具")
    print("=" * 50)
    
    user_input = UserInput()
    
    ref_file = user_input.get_reference_file()
    ref_columns = ExcelHandler.get_columns(ref_file)
    if not ref_columns:
        print("无法读取参照文件列名")
        return
    
    print(f"\n参照文件 '{os.path.basename(ref_file)}' 的列:")
    ref_col_idx = user_input.get_reference_column(ref_columns)
    ref_column_name = ref_columns[ref_col_idx]
    print(f"已选择: {ref_column_name}")
    
    ref_df = ExcelHandler.read_excel(ref_file)
    ref_values = ExcelHandler.get_column_values(ref_df, ref_column_name)
    print(f"参照值数量: {len(ref_values)}")
    
    print("\n" + "-" * 50)
    target_file = user_input.get_target_file()
    target_columns = ExcelHandler.get_columns(target_file)
    if not target_columns:
        print("无法读取目标文件列名")
        return
    
    print(f"\n目标文件 '{os.path.basename(target_file)}' 的列:")
    match_col_idx = user_input.get_match_column(target_columns)
    match_column_name = target_columns[match_col_idx]
    print(f"已选择: {match_column_name}")
    
    fuzzy_match = user_input.ask_fuzzy_match()
    keep_unmatched = user_input.ask_keep_unmatched()
    
    print("\n" + "=" * 50)
    print("开始排序...")
    
    target_df = ExcelHandler.read_excel(target_file)
    print(f"目标文件原始行数: {len(target_df)}")
    
    if fuzzy_match:
        sorted_df = SortLogic.fuzzy_sort_by_reference(
            target_df, ref_values, match_column_name, keep_unmatched
        )
    else:
        sorted_df = SortLogic.sort_by_reference(
            target_df, ref_values, match_column_name, keep_unmatched
        )
    
    print(f"排序后行数: {len(sorted_df)}")
    
    output_path = user_input.get_output_path(target_file)
    if ExcelHandler.write_excel(sorted_df, output_path):
        print(f"\n排序完成！")
        print(f"输出文件: {output_path}")
    else:
        print("\n排序失败！")
    
    if user_input.ask_continue():
        main()

if __name__ == "__main__":
    main()