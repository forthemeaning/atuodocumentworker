"""
检查工具 - 用户脚本
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

def main():
    print("=" * 60)
    print("检查工具 - 用户脚本")
    print("=" * 60)
    
    # === 用户需要修改的部分 ===
    # 请在这里修改您要处理的文件夹路径
    folder_path = r"C:\file\川菜人工智能重点研究室\2026\5月\5.27 23-25结题材料汇总\23-25结题材料汇总"  # 替换为您的文件夹路径
    # ========================
    
    # 检查路径是否存在
    if not os.path.exists(folder_path):
        print(f"错误: 路径不存在 - {folder_path}")
        print("请修改脚本中的 folder_path 变量为有效的文件夹路径")
        return
    
    print(f"目标文件夹: {folder_path}")
    
    # 询问用户要执行的操作
    print("\n请选择操作:")
    print("1. 生成检查配置模板 (生成Excel配置供您填写)")
    print("2. 执行批量检查")
    
    choice = input("\n请输入选择 (1/2): ").strip()
    
    if choice == "1":
        print("\n正在生成检查配置模板...")
        template_path = generate_config_template(folder_path, pattern="")
        if template_path:
            print(f"\n✅ 配置模板已生成: {template_path}")
            print("📝 请打开Excel文件，在'正则表达式'列填写对应的正则表达式")
            print("🔄 然后重新运行脚本选择选项2执行检查")
        else:
            print("❌ 配置模板生成失败")
    
    elif choice == "2":
        config_file = os.path.join(folder_path, "config_template.xlsx")
        if not os.path.exists(config_file):
            print(f"❌ 找不到配置文件: {config_file}")
            print("💡 提示: 请先生成配置（运行脚本并选择选项1），或确保配置文件存在于目标文件夹中")
            return
        
        print(f"\n正在执行批量检查...")
        print(f"使用配置: {config_file}")
        output_folder = os.path.join(script_dir, "result")
        result = batch_check(folder_path, config_file, output_folder=output_folder, dry_run=False)
        
        if result:
            print(f"\n✅ 检查完成!")
            print(f"成功: {result['success']}, 跳过: {result['skip']}, 失败: {result['error']}")
            
            if result['check_list']:
                print(f"\n检查结果 ({min(len(result['check_list']), 10)} 个):")
                for i, item in enumerate(result['check_list']):
                    if i >= 10:
                        print(f"  ... 还有 {len(result['check_list']) - 10} 个")
                        break
                    print(f"  {item['文件名']} -> 匹配内容: {item['匹配内容'][:50]}...")
        else:
            print("❌ 检查失败")
    
    else:
        print("❌ 无效选择")
    
    print("\n" + "=" * 60)
    print("脚本执行完成")

if __name__ == "__main__":
    main()