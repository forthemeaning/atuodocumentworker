"""
使用说明：如何使用检查工具

1. 快速脚本 - quick_check.py
   - 修改脚本顶部的 FOLDER_PATH 变量为目标文件夹路径
   - EXCEL_CONFIG_PATH 可留空（使用默认路径：目标文件夹下的config_template.xlsx）或指定特定路径
   - 运行脚本，选择操作（1-生成配置，2-试运行，3-执行）
   - 检查结果将保存到与原文件夹同级的 "checked" 文件夹中

2. 用户脚本 - user_check.py
   - 修改脚本中的 folder_path 变量为目标文件夹路径
   - 运行脚本，交互式选择操作
   - 检查结果将保存到与原文件夹同级的 "checked" 文件夹中

示例：

假设要处理 D:\MyDocuments 文件夹中的文件：

对于 quick_check.py:
# 修改这两行：
FOLDER_PATH = r"D:\MyDocuments"
EXCEL_CONFIG_PATH = r""  # 留空表示使用 D:\MyDocuments\config_template.xlsx

或者指定具体配置路径：
EXCEL_CONFIG_PATH = r"D:\MyDocuments\my_custom_config.xlsx"

对于 user_check.py:
# 修改这行：
folder_path = r"D:\MyDocuments"

然后运行：
python quick_check.py
或
python user_check.py

检查后的结果将出现在 D:\checked 文件夹中（与 D:\MyDocuments 同级）。
"""