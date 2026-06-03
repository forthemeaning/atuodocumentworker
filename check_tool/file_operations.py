import os
from typing import List

def get_files(folder_path: str, extensions: List[str] = None) -> List[str]:
    """
    递归获取文件夹下指定类型的文件
    
    Args:
        folder_path: 文件夹路径
        extensions: 文件扩展名列表，如 ['.docx', '.doc']，None则返回所有文件
    
    Returns:
        list: 文件完整路径列表
    """
    if extensions is None:
        extensions = ['.docx', '.doc']
    
    files = []
    
    for root, dirs, file_list in os.walk(folder_path):
        for file in file_list:
            if extensions is None or any(file.lower().endswith(ext) for ext in extensions):
                files.append(os.path.join(root, file))
    
    return files


def ensure_folder(folder_path: str) -> bool:
    """
    确保文件夹存在（不存在则创建）
    
    Args:
        folder_path: 文件夹路径
    
    Returns:
        bool: 是否已存在或成功创建
    """
    try:
        os.makedirs(folder_path, exist_ok=True)
        return True
    except Exception:
        return False


def file_exists(file_path: str) -> bool:
    """
    检查文件是否存在
    
    Args:
        file_path: 文件路径
    
    Returns:
        bool: 文件是否存在
    """
    return os.path.exists(file_path)


def folder_exists(folder_path: str) -> bool:
    """
    检查文件夹是否存在
    
    Args:
        folder_path: 文件夹路径
    
    Returns:
        bool: 文件夹是否存在
    """
    return os.path.exists(folder_path) and os.path.isdir(folder_path)