import sys
sys.path.insert(0, 'c:/file/川菜人工智能重点研究室/批处理/sort_tool')

from excel_handler import ExcelHandler
from sort_logic import SortLogic

ref_file = 'c:/file/川菜人工智能重点研究室/批处理/sort_tool/test/reference.xlsx'
target_file = 'c:/file/川菜人工智能重点研究室/批处理/sort_tool/test/target.xlsx'
output_file = 'c:/file/川菜人工智能重点研究室/批处理/sort_tool/test/result.xlsx'

print("=" * 50)
print("排序测试")
print("=" * 50)

ref_df = ExcelHandler.read_excel(ref_file)
print(f"\n参照文件 (期望顺序: 王五, 李四, 张三, 赵六, 陈七):")
print(ref_df)

target_df = ExcelHandler.read_excel(target_file)
print(f"\n目标文件 (原始顺序):")
print(target_df)

ref_values = ExcelHandler.get_column_values(ref_df, '姓名')
print(f"\n参照值列表: {ref_values}")

sorted_df = SortLogic.sort_by_reference(target_df, ref_values, '姓名', keep_unmatched=True)

ExcelHandler.write_excel(sorted_df, output_file)

print(f"\n排序后结果:")
print(sorted_df)
print(f"\n输出文件: {output_file}")
print("\n✅ 测试完成!")