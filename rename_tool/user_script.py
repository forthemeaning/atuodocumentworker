"""
文件重命名工具 - 用户调用脚本
用于快速调用重命名功能，只需修改路径即可使用
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

def main():
    print("=" * 60)
    print("文件重命名工具 - 用户调用脚本")
    print("=" * 60)
    
    # === 用户需要修改的部分 ===
    # 请在这里修改您要处理的文件夹路径
    folder_path = r""  # 替换为您的文件夹路径
    # ========================
    
    # 检查路径是否存在
    if not os.path.exists(folder_path):
        print(f"错误: 路径不存在 - {folder_path}")
        print("请修改脚本中的 folder_path 变量为有效的文件夹路径")
        return
    
    print(f"目标文件夹: {folder_path}")
    
    # 询问用户要执行的操作
    print("\n请选择操作:")
    print("1. 生成重命名模板 (生成Excel模板供您填写)")
    print("2. 执行批量重命名 (使用已有模板)")
    print("3. 试运行批量重命名 (预览结果，不实际执行)")
    
    choice = input("\n请输入选择 (1/2/3): ").strip()
    
    if choice == "1":
        print("\n正在生成重命名模板...")
        template_path = generate_rename_template(folder_path, separator="_")
        if template_path:
            print(f"\n✅ 模板已生成: {template_path}")
            print("📝 请打开Excel文件，填写子名列")
            print("🔄 然后重新运行脚本选择选项2或3执行重命名")
        else:
            print("❌ 模板生成失败")
    
    elif choice == "2":
        # 查找模板文件
        template_file = os.path.join(folder_path, "rename_template.xlsx")
        if not os.path.exists(template_file):
            print(f"❌ 找不到模板文件: {template_file}")
            print("💡 提示: 请先生成模板（运行脚本并选择选项1），或确保模板文件存在于目标文件夹中")
            return
        
        print(f"\n正在执行批量重命名...")
        print(f"使用模板: {template_file}")
        # 设置输出文件夹为同级的result文件夹
        output_folder = os.path.join(os.path.dirname(folder_path), "result")
        result = batch_rename(folder_path, template_file, output_folder=output_folder, dry_run=False)
        
        if result:
            print(f"\n✅ 批量重命名完成!")
            print(f"成功: {result['success']}, 跳过: {result['skip']}, 失败: {result['error']}")
            print(f"重命名记录已保存到: {os.path.join(folder_path, 'rename_log.xlsx')}")
        else:
            print("❌ 批量重命名失败")
    
    elif choice == "3":
        # 查找模板文件
        template_file = os.path.join(folder_path, "rename_template.xlsx")
        if not os.path.exists(template_file):
            print(f"❌ 找不到模板文件: {template_file}")
            print("💡 提示: 请先生成模板（运行脚本并选择选项1），或确保模板文件存在于目标文件夹中")
            return
        
        print(f"\n正在试运行批量重命名 (仅预览)...")
        print(f"使用模板: {template_file}")
        # 设置输出文件夹为同级的result文件夹
        output_folder = os.path.join(os.path.dirname(folder_path), "result")
        result = batch_rename(folder_path, template_file, output_folder=output_folder, dry_run=True)
        
        if result:
            print(f"\n✅ 试运行完成! 以下是预览结果:")
            print(f"成功: {result['success']}, 跳过: {result['skip']}, 失败: {result['error']}")
            print("📝 实际文件不会被修改")
            print("🔄 如需实际执行，请选择选项2")
            
            # 显示重命名预览
            if result['rename_list']:
                print(f"\n预览重命名 ({min(len(result['rename_list']), 10)} 个):")
                for i, item in enumerate(result['rename_list']):
                    if i >= 10:  # 只显示前10个
                        print(f"  ... 还有 {len(result['rename_list']) - 10} 个")
                        break
                    print(f"  {item['原文件名']} -> {item['新文件名']}")
        else:
            print("❌ 试运行失败")
    
    else:
        print("❌ 无效选择")
    
    print("\n" + "=" * 60)
    print("脚本执行完成")

if __name__ == "__main__":
    main()