import os
import pandas as pd
from typing import List, Dict, Any, Optional

# 支持直接运行和作为模块导入
try:
    from .file_operations import get_files, copy_file, ensure_folder, file_exists, folder_exists
    from .excel_handler import ExcelHandler
except ImportError:
    # 当直接运行或作为模块导入时
    from file_operations import get_files, copy_file, ensure_folder, file_exists, folder_exists
    from excel_handler import ExcelHandler


class RenameTemplateGenerator:
    """重命名模板生成器"""
    
    def __init__(self, separator: str = " "):
        self.separator = separator
    
    def generate(self, folder_path: str, output_path: Optional[str] = None) -> Optional[str]:
        """
        生成文件重命名模板Excel
        
        Args:
            folder_path: 文件所在文件夹路径
            output_path: 模板输出路径（默认为文件夹下的 rename_template.xlsx）
        
        Returns:
            str: 生成的模板文件路径
        """
        print("=" * 70)
        print("生成文件重命名模板...")
        print("=" * 70)
        
        if not folder_exists(folder_path):
            print(f"错误：文件夹不存在 - {folder_path}")
            return None
        
        files = get_files(folder_path)
        print(f"找到 {len(files)} 个文件")
        
        if not files:
            print("未找到文件")
            return None
        
        template_data = self._build_template_data(files)
        
        if output_path is None:
            output_path = os.path.join(folder_path, "rename_template.xlsx")
        
        if ExcelHandler.write_excel(template_data, output_path):
            self._print_success_info(output_path, len(files))
            return output_path
        
        return None
    
    def _build_template_data(self, files: List[str]) -> List[Dict[str, Any]]:
        """
        构建模板数据
        
        Args:
            files: 文件路径列表
        
        Returns:
            list: 模板数据列表
        """
        template_data = []
        for file_path in files:
            file_name = os.path.basename(file_path)
            file_ext = os.path.splitext(file_name)[1]
            
            template_data.append({
                '原文件名': file_name,
                '子名1': '',
                '子名2': '',
                '子名3': '',
                '连接符': self.separator,
                '新文件名': '',
                '文件扩展名': file_ext,
                '文件路径': file_path
            })
        
        return template_data
    
    def _print_success_info(self, output_path: str, file_count: int):
        """
        打印成功信息
        
        Args:
            output_path: 输出路径
            file_count: 文件数量
        """
        print(f"\n模板已生成: {output_path}")
        print(f"共 {file_count} 个文件")
        print("\n请打开Excel文件，填写'子名'列")
        print("新文件名将自动生成为：子名1 + 连接符 + 子名2 + 连接符 + 子名3 + ... + 文件扩展名")
        print("空的子名不会被连接，如果所有子名都为空则保持原文件名")
        print("也可以直接在'新文件名'列手动填写")
        print("填写完成后，使用该文件执行批量重命名")
        print("=" * 70)


class BatchRenamer:
    """批量重命名处理器"""
    
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
    
    def rename(self, folder_path: str, excel_path: str, output_folder: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        批量重命名文件（增量处理）
        
        Args:
            folder_path: 原文件所在文件夹路径
            excel_path: 配置Excel路径
            output_folder: 输出文件夹路径（默认为原文件夹下的 renamed 文件夹）
        
        Returns:
            dict: 重命名结果统计
        """
        print("=" * 70)
        print("批量重命名文件...")
        print("=" * 70)
        
        if not folder_exists(folder_path):
            print(f"错误：文件夹不存在 - {folder_path}")
            return None
        
        df = ExcelHandler.read_excel(excel_path)
        if df is None:
            return None
        
        print(f"读取到 {len(df)} 条配置")
        
        df_valid = ExcelHandler.filter_valid_rows(df, ['新文件名', '子名1', '子名2', '子名3', '子名4', '子名5', '子名6', '子名7', '子名8', '子名9', '子名10'])
        print(f"有效配置 {len(df_valid)} 条")
        
        if len(df_valid) == 0:
            print("没有有效的重命名配置")
            return None
        
        if output_folder is None:
            output_folder = os.path.join(os.path.dirname(__file__), "result")
        
        if not self.dry_run:
            ensure_folder(output_folder)
            print(f"输出文件夹: {output_folder}")
        else:
            print(f"[试运行模式] 将输出到: {output_folder}")
        
        result = self._execute_rename(df_valid, output_folder)
        
        if result['rename_list']:
            self._save_log(folder_path, result['rename_list'])
        
        self._print_statistics(result, output_folder)
        
        return result
    
    def _execute_rename(self, df: pd.DataFrame, output_folder: str) -> Dict[str, Any]:
        """
        执行重命名操作
        
        Args:
            df: 有效配置数据框
            output_folder: 输出文件夹
        
        Returns:
            dict: 重命名结果
        """
        success_count = 0
        skip_count = 0
        error_count = 0
        rename_list = []
        
        for idx, row in df.iterrows():
            old_name = row['原文件名']
            old_path = row['文件路径']
            file_ext = row['文件扩展名']
            
            new_name = self._generate_new_name(row, file_ext)
            
            if not new_name or new_name == file_ext:
                print(f"跳过: {old_name} (新文件名为空)")
                skip_count += 1
                continue
            
            new_path = os.path.join(output_folder, new_name)
            
            if not file_exists(old_path):
                print(f"错误: 原文件不存在 - {old_path}")
                error_count += 1
                continue
            
            if file_exists(new_path):
                print(f"跳过: {old_name} -> {new_name} (目标文件已存在)")
                skip_count += 1
                continue
            
            rename_list.append({
                '原文件名': old_name,
                '新文件名': new_name,
                '原路径': old_path,
                '新路径': new_path
            })
            
            if self.dry_run:
                print(f"[试运行] {old_name} -> {new_name}")
            else:
                if copy_file(old_path, new_path):
                    print(f"成功: {old_name} -> {new_name}")
                    success_count += 1
                else:
                    print(f"失败: {old_name} -> {new_name}")
                    error_count += 1
        
        return {
            'success': success_count,
            'skip': skip_count,
            'error': error_count,
            'total': len(rename_list),
            'rename_list': rename_list
        }
    
    def _generate_new_name(self, row: pd.Series, file_ext: str) -> str:
        """
        生成新文件名
        
        Args:
            row: 数据行
            file_ext: 文件扩展名
        
        Returns:
            str: 新文件名
        """
        new_name = row['新文件名']
        
        if pd.isna(new_name) or new_name == '':
            # 获取所有子名字段
            sub_names = []
            for i in range(1, 100):  # 支持子名1到子名99，足够使用
                sub_field = f'子名{i}'
                if sub_field in row:
                    sub_value = str(row[sub_field]) if pd.notna(row[sub_field]) else ''
                    if sub_value.strip():  # 只添加非空的子名
                        sub_names.append(sub_value)
                else:
                    # 如果当前子名字段不存在，则停止查找
                    break
            
            if sub_names:  # 如果有非空子名
                separator = str(row['连接符']) if pd.notna(row['连接符']) else '_'
                new_name = separator.join(sub_names) + file_ext
            else:  # 如果所有子名都为空，保持原文件名
                original_filename = row['原文件名']
                new_name = original_filename
        
        return new_name
    
    def _save_log(self, folder_path: str, rename_list: List[Dict[str, Any]]):
        """
        保存重命名记录
        
        Args:
            folder_path: 文件夹路径
            rename_list: 重命名列表
        """
        log_path = os.path.join(folder_path, "rename_log.xlsx")
        if ExcelHandler.write_excel(rename_list, log_path):
            print(f"\n重命名记录已保存: {log_path}")
    
    def _print_statistics(self, result: Dict[str, Any], output_folder: str):
        """
        打印统计信息
        
        Args:
            result: 重命名结果
            output_folder: 输出文件夹
        """
        print("\n" + "=" * 70)
        print("重命名统计:")
        print(f"  成功: {result['success']}")
        print(f"  跳过: {result['skip']}")
        print(f"  失败: {result['error']}")
        print(f"  总计: {result['total']}")
        
        if self.dry_run:
            print("\n[试运行模式] 未实际执行重命名")
            print("如需执行，请设置 dry_run=False")
        else:
            print(f"\n文件已复制到: {output_folder}")
        
        print("=" * 70)