import os
import shutil
from typing import List, Optional


def get_files(folder_path: str, extensions: Optional[List[str]] = None) -> List[str]:
    """
    获取文件夹中的文件
    
    Args:
        folder_path: 文件夹路径
        extensions: 文件扩展名列表（None表示仅获取Word和PDF文件，空列表[]表示所有文件）
    
    Returns:
        list: 文件完整路径列表
    """
    if extensions is None:
        extensions = ['.doc', '.docx', '.pdf']
    
    files = []
    
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path):
            if not extensions or any(file.lower().endswith(ext) for ext in extensions):
                files.append(file_path)
    
    return files


def copy_file(src_path: str, dst_path: str) -> bool:
    """
    复制文件
    
    Args:
        src_path: 源文件路径
        dst_path: 目标文件路径
    
    Returns:
        bool: 是否成功
    """
    try:
        shutil.copy2(src_path, dst_path)
        return True
    except Exception as e:
        print(f"复制文件失败: {e}")
        return False


def ensure_folder(folder_path: str) -> bool:
    """
    确保文件夹存在
    
    Args:
        folder_path: 文件夹路径
    
    Returns:
        bool: 是否成功
    """
    try:
        os.makedirs(folder_path, exist_ok=True)
        return True
    except Exception as e:
        print(f"创建文件夹失败: {e}")
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
    return os.path.exists(folder_path)