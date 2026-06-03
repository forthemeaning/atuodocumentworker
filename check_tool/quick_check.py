"""
检查工具 - 快速脚本
用于快速调用检查功能，只需修改路径即可使用
"""

import os
import sys
from pathlib import Path

# 添加当前目录到Python路径
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

# 直接导入模块而不是使用相对导入
import check_main
from check_main import generate_config_template, batch_check

# === 请在此修改路径 ===
FOLDER_PATH = r"C:\file\川菜人工智能重点研究室\2026\5月\5.27 23-25结题材料汇总\23-25结题材料汇总"  # 修改为目标文件夹路径
EXCEL_CONFIG_PATH = r""  # 修改为配置文件路径（留空则使用默认路径：目标文件夹下的config_template.xlsx）
# ====================

def main():
    print("快速检查脚本")
    print(f"目标文件夹: {FOLDER_PATH}")
    
    if not os.path.exists(FOLDER_PATH):
        print(f"❌ 路径不存在: {FOLDER_PATH}")
        print("请修改脚本中的 FOLDER_PATH 变量")
        return
    
    print("\n选择操作:")
    print("1. 生成配置模板 (generate_config)")
    print("2. 执行检查 (execute)")
    
    choice = input("输入选择 (1/2): ").strip()
    
    if choice == "1":
        print("正在生成配置模板...")
        result = generate_config_template(FOLDER_PATH, pattern="")
        if result:
            print(f"✅ 配置模板已生成: {result}")
        else:
            print("❌ 配置模板生成失败")
    
    elif choice == "2":
        if not EXCEL_CONFIG_PATH.strip():
            excel_path = os.path.join(FOLDER_PATH, "config_template.xlsx")
        else:
            excel_path = EXCEL_CONFIG_PATH
        
        if not os.path.exists(excel_path):
            print(f"❌ 配置文件不存在: {excel_path}")
            print("💡 提示: 请先选择选项 1 生成配置")
            return
            
        print(f"使用配置: {excel_path}")
        print("正在执行检查...")
        output_folder = os.path.join(script_dir, "result")
        result = batch_check(FOLDER_PATH, excel_path, output_folder=output_folder, dry_run=False)
        if result:
            print(f"✅ 检查完成 - 成功: {result['success']}, 跳过: {result['skip']}, 失败: {result['error']}")
        else:
            print("❌ 检查失败")
    
    else:
        print("❌ 无效选择")

if __name__ == "__main__":
    main()