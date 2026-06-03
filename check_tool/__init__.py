"""
检查工具 - 模块初始化

支持以下导入方式：
from check_tool import generate_config_template, batch_check
"""

from .check_processor import ConfigTemplateGenerator, BatchChecker

def generate_config_template(folder_path, output_path=None, pattern=""):
    """
    生成配置模板
    
    Args:
        folder_path: 文件所在文件夹路径
        output_path: 模板输出路径（默认为文件夹下的 config_template.xlsx）
        pattern: 默认正则表达式
    
    Returns:
        str: 生成的模板文件路径
    """
    generator = ConfigTemplateGenerator(pattern=pattern)
    return generator.generate(folder_path, output_path)


def batch_check(folder_path, excel_path, output_folder=None, dry_run=True):
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