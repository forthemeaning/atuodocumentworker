import os
from typing import Optional, Dict, Any

# 支持直接运行和作为模块导入
try:
    from .rename_logic import RenameTemplateGenerator, BatchRenamer
except ImportError:
    # 当直接运行或作为模块导入时
    from rename_logic import RenameTemplateGenerator, BatchRenamer


def generate_rename_template(folder_path: str, output_path: Optional[str] = None, separator: str = "_") -> Optional[str]:
    """
    生成文件重命名模板Excel
    
    Args:
        folder_path: 文件所在文件夹路径
        output_path: 模板输出路径（默认为文件夹下的 rename_template.xlsx）
        separator: 默认连接符
    
    Returns:
        str: 生成的模板文件路径
    """
    generator = RenameTemplateGenerator(separator=separator)
    return generator.generate(folder_path, output_path)


def batch_rename(folder_path: str, excel_path: str, output_folder: Optional[str] = None, dry_run: bool = True) -> Optional[Dict[str, Any]]:
    """
    批量重命名文件（增量处理）
    
    Args:
        folder_path: 原文件所在文件夹路径
        excel_path: 配置Excel路径
        output_folder: 输出文件夹路径（默认为原文件夹下的 renamed 文件夹）
        dry_run: 是否为试运行（True只显示不执行，False执行重命名）
    
    Returns:
        dict: 重命名结果统计
    """
    renamer = BatchRenamer(dry_run=dry_run)
    return renamer.rename(folder_path, excel_path, output_folder)


# ========== 使用入口 ==========
if __name__ == "__main__":
    test_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test")
    
    print("测试模式：生成test文件夹的重命名模板")
    generate_rename_template(test_folder, separator="_")