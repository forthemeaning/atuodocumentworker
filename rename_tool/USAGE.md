"""
使用说明：如何使用重命名工具

1. 快速脚本 - quick_rename.py
   - 修改脚本顶部的 FOLDER_PATH 变量为目标文件夹路径
   - EXCEL_TEMPLATE_PATH 可留空（使用默认路径：目标文件夹下的rename_template.xlsx）或指定特定路径
   - 运行脚本，选择操作（1-生成模板，2-试运行，3-执行）
   - 重命名结果将保存到与原文件夹同级的 "result" 文件夹中

2. 用户脚本 - user_script.py
   - 修改脚本中的 folder_path 变量为目标文件夹路径
   - 运行脚本，交互式选择操作
   - 重命名结果将保存到与原文件夹同级的 "result" 文件夹中

示例：

假设要处理 D:\MyDocuments 文件夹中的文件：

对于 quick_rename.py:
# 修改这两行：
FOLDER_PATH = r"D:\MyDocuments"
EXCEL_TEMPLATE_PATH = r""  # 留空表示使用 D:\MyDocuments\rename_template.xlsx

或者指定具体模板路径：
EXCEL_TEMPLATE_PATH = r"D:\MyDocuments\my_custom_template.xlsx"

对于 user_script.py:
# 修改这行：
folder_path = r"D:\MyDocuments"

然后运行：
python quick_rename.py
或
python user_script.py

重命名后的文件将出现在 D:\result 文件夹中（与 D:\MyDocuments 同级）。
"""