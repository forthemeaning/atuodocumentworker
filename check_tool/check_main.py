import os
from typing import Optional, Dict, Any

# 支持直接运行和作为模块导入
try:
    from .check_processor import ConfigTemplateGenerator, BatchChecker
except ImportError:
    # 当直接运行或作为模块导入时
    from check_processor import ConfigTemplateGenerator, BatchChecker


def generate_config_template(folder_path: str, output_path: Optional[str] = None, pattern: str = "") -> Optional[str]:
    """
    生成文件检查配置模板Excel
    
    Args:
        folder_path: 文件所在文件夹路径
        output_path: 模板输出路径（默认为文件夹下的 config_template.xlsx）
        pattern: 默认正则表达式
    
    Returns:
        str: 生成的模板文件路径
    """
    generator = ConfigTemplateGenerator(pattern=pattern)
    return generator.generate(folder_path, output_path)


def batch_check(folder_path: str, excel_path: str, output_folder: Optional[str] = None, dry_run: bool = True) -> Optional[Dict[str, Any]]:
    """
    批量检查文件（增量处理）
    
    Args:
        folder_path: 原文件所在文件夹路径
        excel_path: 配置Excel路径
        output_folder: 输出文件夹路径（默认为原文件夹下的 checked 文件夹）
        dry_run: 是否为试运行（True只显示不执行，False执行检查）
    
    Returns:
        dict: 检查结果统计
    """
    checker = BatchChecker(dry_run=dry_run)
    return checker.check(folder_path, excel_path, output_folder)


# ========== 使用入口 ==========
if __name__ == "__main__":
    test_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test")
    
    print("测试模式：生成test文件夹的配置模板")
    generate_config_template(test_folder, pattern="")