import os

class UserInput:
    """用户输入处理"""
    
    def __init__(self, config_file: str = "sort_config.txt"):
        self.config_file = config_file
    
    def get_reference_file(self) -> str:
        """获取参照文件路径"""
        path = input("请输入参照Excel文件路径（仅一列作为排序依据）: ").strip()
        if not path:
            print("路径不能为空")
            return self.get_reference_file()
        if not os.path.exists(path):
            print(f"文件不存在: {path}")
            return self.get_reference_file()
        return path
    
    def get_target_file(self) -> str:
        """获取目标文件路径"""
        path = input("请输入待排序Excel文件路径: ").strip()
        if not path:
            print("路径不能为空")
            return self.get_target_file()
        if not os.path.exists(path):
            print(f"文件不存在: {path}")
            return self.get_target_file()
        return path
    
    def get_reference_column(self, columns: list) -> int:
        """获取参照列索引（从1开始）"""
        print(f"\n可用列: {columns}")
        try:
            idx = int(input(f"请输入参照列序号（1-{len(columns)}）: ").strip())
            if 1 <= idx <= len(columns):
                return idx - 1
            print(f"序号超出范围，请输入1-{len(columns)}之间的数字")
            return self.get_reference_column(columns)
        except ValueError:
            print("请输入有效的数字")
            return self.get_reference_column(columns)
    
    def get_match_column(self, columns: list) -> int:
        """获取匹配列索引"""
        print(f"\n可用列: {columns}")
        try:
            idx = int(input(f"请输入匹配列序号（1-{len(columns)}）: ").strip())
            if 1 <= idx <= len(columns):
                return idx - 1
            print(f"序号超出范围，请输入1-{len(columns)}之间的数字")
            return self.get_match_column(columns)
        except ValueError:
            print("请输入有效的数字")
            return self.get_match_column(columns)
    
    def get_output_path(self, target_path: str) -> str:
        """获取输出文件路径"""
        default_name = target_path.replace('.xlsx', '_sorted.xlsx')
        path = input(f"请输入输出文件路径（直接回车使用默认: {default_name}）: ").strip()
        if not path:
            return default_name
        return path
    
    def ask_fuzzy_match(self) -> bool:
        """询问是否使用模糊匹配"""
        answer = input("是否使用模糊匹配？（y/n，直接回车默认n）: ").strip().lower()
        return answer == 'y'
    
    def ask_keep_unmatched(self) -> bool:
        """询问是否保留未匹配行"""
        answer = input("是否保留未匹配的行？（y/n，直接回车默认y）: ").strip().lower()
        return answer != 'n'
    
    def ask_continue(self) -> bool:
        """询问是否继续"""
        answer = input("\n是否继续？（y/n）: ").strip().lower()
        return answer == 'y'
    
    def save_config(self, config: dict):
        """保存配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            for key, value in config.items():
                f.write(f"{key}={value}\n")
    
    def load_config(self) -> dict:
        """加载配置"""
        config = {}
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        config[key] = value
        return config