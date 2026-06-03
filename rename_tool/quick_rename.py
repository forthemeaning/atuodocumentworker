"""
快速重命名脚本 - 仅需修改路径
"""

import os
import sys
from pathlib import Path

# 添加当前目录到Python路径
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

# 直接导入模块而不是使用相对导入
import file_rename
from file_rename import generate_rename_template, batch_rename

# === 请在此修改路径 ===
FOLDER_PATH = r"C:\file\川菜人工智能重点研究室\批处理\rename_tool\test"  # 修改为目标文件夹路径
EXCEL_TEMPLATE_PATH = r""
# ====================

def main():
    print("快速重命名脚本")
    print(f"目标文件夹: {FOLDER_PATH}")
    
    if not os.path.exists(FOLDER_PATH):
        print(f"❌ 路径不存在: {FOLDER_PATH}")
        print("请修改脚本中的 FOLDER_PATH 变量")
        return
    
    print("\n选择操作:")
    print("1. 生成模板 (generate_template)")
    print("2. 试运行重命名 (dry_run)")
    print("3. 执行重命名 (execute)")
    
    choice = input("输入选择 (1/2/3): ").strip()
    
    if choice == "1":
        print("正在生成模板...")
        result = generate_rename_template(FOLDER_PATH, separator="_")
        if result:
            print(f"✅ 模板已生成: {result}")
        else:
            print("❌ 模板生成失败")
    
    elif choice == "2":
        # 如果没有指定Excel路径，则使用默认模板
        if not EXCEL_TEMPLATE_PATH.strip():  # 如果模板路径为空或只包含空白字符
            excel_path = os.path.join(FOLDER_PATH, "rename_template.xlsx")
        else:
            excel_path = EXCEL_TEMPLATE_PATH
        
        if not os.path.exists(excel_path):
            print(f"❌ Excel模板不存在: {excel_path}")
            print("💡 提示: 请先选择选项 1 生成模板，或修改脚本中的 EXCEL_TEMPLATE_PATH 变量")
            return
            
        print(f"使用模板: {excel_path}")
        print("正在试运行重命名...")
        # 设置输出文件夹为同级的result文件夹
        output_folder = os.path.join(os.path.dirname(FOLDER_PATH), "result")
        result = batch_rename(FOLDER_PATH, excel_path, output_folder=output_folder, dry_run=True)
        if result:
            print(f"✅ 试运行完成 - 成功: {result['success']}, 跳过: {result['skip']}, 失败: {result['error']}")
        else:
            print("❌ 试运行失败")
    
    elif choice == "3":
        # 如果没有指定Excel路径，则使用默认模板
        if not EXCEL_TEMPLATE_PATH.strip():  # 如果模板路径为空或只包含空白字符
            excel_path = os.path.join(FOLDER_PATH, "rename_template.xlsx")
        else:
            excel_path = EXCEL_TEMPLATE_PATH
        
        if not os.path.exists(excel_path):
            print(f"❌ Excel模板不存在: {excel_path}")
            print("💡 提示: 请先选择选项 1 生成模板，或修改脚本中的 EXCEL_TEMPLATE_PATH 变量")
            return
            
        print(f"使用模板: {excel_path}")
        print("正在执行重命名...")
        # 设置输出文件夹为同级的result文件夹
        output_folder = os.path.join(os.path.dirname(FOLDER_PATH), "result")
        result = batch_rename(FOLDER_PATH, excel_path, output_folder=output_folder, dry_run=False)
        if result:
            print(f"✅ 重命名完成 - 成功: {result['success']}, 跳过: {result['skip']}, 失败: {result['error']}")
        else:
            print("❌ 重命名失败")
    
    else:
        print("❌ 无效选择")

if __name__ == "__main__":
    main()