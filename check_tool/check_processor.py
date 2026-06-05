import os
import pandas as pd
from typing import List, Dict, Any, Optional
import re

# 支持直接运行和作为模块导入
try:
    from .file_operations import get_files, ensure_folder, file_exists, folder_exists
    from .excel_handler import ExcelHandler
except ImportError:
    # 当直接运行或作为模块导入时
    from file_operations import get_files, ensure_folder, file_exists, folder_exists
    from excel_handler import ExcelHandler

# 不预先导入win32com，而是在需要时再导入
WIN32COM_AVAILABLE = None

def check_win32com_availability():
    """检查win32com是否可用"""
    global WIN32COM_AVAILABLE
    if WIN32COM_AVAILABLE is None:
        try:
            import win32com.client
            import pythoncom
            WIN32COM_AVAILABLE = True
        except ImportError:
            WIN32COM_AVAILABLE = False
    return WIN32COM_AVAILABLE


def get_match_pages_com(file_path: str, pattern: str) -> List[Dict[str, Any]]:
    """使用WPS COM接口获取匹配文本的页码"""
    if not check_win32com_availability():
        print("❌ win32com.client 不可用，无法使用WPS COM接口")
        return []
        
    import win32com.client  # 延迟导入
    import pythoncom

    pythoncom.CoInitialize()  # 初始化 COM 线程（Flask 多线程环境下必需）

    word = None
    doc = None
    results = []

    # 检查文件是否存在
    if not file_exists(file_path):
        print(f"文件不存在: {file_path}")
        pythoncom.CoUninitialize()
        return []

    try:
        # 连接 WPS（关键：使用 KWPS.Application 而不是 Word.Application）
        word = win32com.client.Dispatch("KWPS.Application")
        word.Visible = False
        word.DisplayAlerts = 0  # 不显示警告对话框
        
        # 打开文档
        print(f"正在打开文档: {file_path}")
        doc = word.Documents.Open(file_path)
        
        if not doc:
            print("文档打开失败")
            return []
        
        # 遍历所有段落
        paragraph_count = doc.Paragraphs.Count
        print(f"文档共 {paragraph_count} 个段落，正在搜索...")
        
        for i in range(1, paragraph_count + 1):
            paragraph = doc.Paragraphs(i)
            para_text = paragraph.Range.Text
            
            # 在当前段落中搜索匹配项
            for match in re.finditer(pattern, para_text):
                match_text = match.group()
                match_start = match.start()
                
                try:
                    # 创建定位到匹配文本的 Range 对象
                    rng = paragraph.Range
                    rng.Start = paragraph.Range.Start + match_start
                    rng.End = rng.Start + len(match_text)
                    
                    # 获取页码（3 = wdActiveEndAdjustedPageNumber）
                    page_num = rng.Information(3)
                    
                    # 去重：避免同一位置重复添加
                    duplicate = False
                    for existing in results:
                        if existing['page'] == page_num and existing['text'] == match_text:
                            duplicate = True
                            break
                    
                    if not duplicate:
                        results.append({
                            'text': match_text,
                            'page': page_num
                        })
                        print(f"  找到匹配: 第{page_num}页 - {match_text[:40]}...")
                        
                except Exception as e:
                    print(f"  处理段落 {i} 时出错: {e}")
                    continue
                    
    except Exception as e:
        print(f"处理出错：{e}")
        import traceback
        traceback.print_exc()
        return []
        
    finally:
        # 安全关闭文档和退出WPS
        try:
            if doc:
                doc.Close(False)
        except:
            pass

        try:
            if word:
                word.Quit()
        except:
            pass

        try:
            pythoncom.CoUninitialize()
        except:
            pass
    
    return results


class ConfigTemplateGenerator:
    """配置模板生成器"""
    
    def __init__(self, pattern: str = ""):
        """
        初始化
        
        Args:
            pattern: 默认正则表达式
        """
        self.pattern = pattern
    
    def generate(self, folder_path: str, output_path: Optional[str] = None) -> Optional[str]:
        """
        生成配置模板
        
        Args:
            folder_path: Word文件所在文件夹路径
            output_path: 配置文件输出路径（默认为文件夹下的 config_template.xlsx）
        
        Returns:
            str: 生成的配置文件路径
        """
        print("=" * 70)
        print("生成配置模板...")
        print("=" * 70)
        
        # 1. 验证文件夹
        if not folder_exists(folder_path):
            print(f"错误：文件夹不存在 - {folder_path}")
            return None
        
        # 2. 获取所有Word文件
        word_files = get_files(folder_path, ['.docx', '.doc'])
        print(f"找到 {len(word_files)} 个Word文件")
        
        if not word_files:
            print("未找到Word文件")
            return None
        
        # 3. 生成模板数据
        template_data = self._build_template_data(word_files)
        
        # 4. 保存到Excel
        if output_path is None:
            output_path = os.path.join(folder_path, "config_template.xlsx")
        
        success = ExcelHandler.write_excel(
            template_data, 
            output_path, 
            columns=['原文件名', '文件路径', '正则表达式', '文件扩展名']
        )
        
        if success:
            self._print_success_info(output_path, len(word_files))
            return output_path
        else:
            print("生成配置模板失败")
            return None
    
    def _build_template_data(self, files: List[str]) -> List[Dict[str, Any]]:
        """构建模板数据"""
        template_data = []
        for file_path in files:
            file_name = os.path.basename(file_path)
            file_ext = os.path.splitext(file_name)[1]
            
            template_data.append({
                '原文件名': file_name,
                '文件路径': file_path,
                '正则表达式': self.pattern,
                '文件扩展名': file_ext
            })
        
        return template_data
    
    def _print_success_info(self, output_path: str, file_count: int):
        """打印成功信息"""
        print(f"\n配置模板已生成: {output_path}")
        print(f"共 {file_count} 个文件")
        print("\n请打开Excel文件，在'正则表达式'列填写对应的正则表达式")
        print("填写完成后，使用该文件作为配置文件运行批量检查")
        print("=" * 70)


class BatchChecker:
    """批量检查器"""
    
    def __init__(self, dry_run: bool = False):
        """
        初始化
        
        Args:
            dry_run: 是否为试运行
        """
        self.dry_run = dry_run
    
    def check(self, folder_path: str, excel_path: str, output_folder: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        批量检查文件
        
        Args:
            folder_path: 原文件所在文件夹路径
            excel_path: 配置Excel路径
            output_folder: 输出文件夹路径（默认为原文件夹下的 checked 文件夹）
        
        Returns:
            dict: 检查结果统计
        """
        print("=" * 70)
        print("批量检查文件...")
        print("=" * 70)
        
        if not folder_exists(folder_path):
            print(f"错误：文件夹不存在 - {folder_path}")
            return None
        
        df = ExcelHandler.read_excel(excel_path)
        if df is None:
            return None
        
        # 过滤有效配置
        df_valid = ExcelHandler.filter_valid_rows(df, ['正则表达式'])
        print(f"有效配置 {len(df_valid)} 条")
        
        if len(df_valid) == 0:
            print("没有有效的检查配置")
            return None
        
        result = self._execute_check(df_valid, folder_path, output_folder)
        
        self._print_statistics(result)
        
        return result
    
    def _execute_check(self, df: pd.DataFrame, folder_path: str, output_folder: Optional[str] = None) -> Dict[str, Any]:
        """执行检查"""
        if output_folder is None:
            output_folder = os.path.join(os.path.dirname(__file__), "result")
        
        if not self.dry_run:
            ensure_folder(output_folder)
            print(f"输出文件夹: {output_folder}")
        else:
            print(f"[试运行模式] 将输出到: {output_folder}")
        
        # 执行检查逻辑
        check_results = []
        success_count = 0
        skip_count = 0
        error_count = 0
        
        # 获取所有Word文件
        word_files = get_files(folder_path, ['.docx', '.doc'])
        print(f"找到 {len(word_files)} 个Word文件")
        
        for idx, file_path in enumerate(word_files, 1):
            file_name = os.path.basename(file_path)
            print(f"[{idx}/{len(word_files)}] 正在检查: {file_name}")
            
            # 查找该文件对应的正则
            matched_regex = None
            for _, row in df.iterrows():
                config_file_name = row['原文件名'] if '原文件名' in row else row['文件名']
                regex_pattern = row['正则表达式']
                
                # 支持精确匹配或包含匹配
                if config_file_name == file_name or config_file_name in file_name:
                    matched_regex = regex_pattern
                    print(f"    匹配到规则: {config_file_name}")
                    break
            
            if matched_regex is None or pd.isna(matched_regex) or matched_regex == '':
                print(f"    未找到对应的正则规则或规则为空，跳过")
                skip_count += 1
                continue
            
            # 使用对应的正则进行搜索
            matches = get_match_pages_com(file_path, matched_regex)
            
            for match in matches:
                check_results.append({
                    '文件名': file_name,
                    '文件路径': file_path,
                    '正则表达式': matched_regex,
                    '匹配内容': match.get('text', match),
                    '页码': match.get('page', match.get('页码', '')),
                    '位置信息': match.get('position', '')
                })
            
            if matches:
                success_count += 1
                print(f"    找到 {len(matches)} 处匹配")
            else:
                print(f"    未找到匹配内容")
        
        # 保存结果（无论是否有匹配内容都保存）
        result_path = os.path.join(output_folder, "check_result.xlsx")
        if not self.dry_run:
            # 确保输出文件夹存在
            if not ensure_folder(output_folder):
                print(f"❌ 无法创建输出文件夹: {output_folder}")
                return {
                    'check_list': check_results,
                    'success': success_count,
                    'skip': skip_count,
                    'error': error_count + 1,
                    'total': len(word_files)
                }
            
            # 添加统计信息到结果中
            summary_data = [{
                '文件名': '【统计汇总】',
                '文件路径': '',
                '正则表达式': '',
                '匹配内容': f"成功: {success_count}, 跳过: {skip_count}, 失败: {error_count}, 总计: {len(word_files)}",
                '页码': '',
                '位置信息': ''
            }]
            all_data = summary_data + check_results
            
            # 保存到Excel
            if ExcelHandler.write_excel(all_data, result_path):
                print(f"✅ 检查结果已保存至: {result_path}")
            else:
                print(f"❌ 保存结果失败: {result_path}")
        
        return {
            'check_list': check_results,
            'success': success_count,
            'skip': skip_count,
            'error': error_count,
            'total': len(word_files)
        }
    
    def _print_statistics(self, result: Dict[str, Any]):
        """打印统计信息"""
        if result is None:
            print("❌ 检查失败")
            return
        
        print("=" * 70)
        print("检查统计:")
        print(f"  成功: {result['success']}")
        print(f"  跳过: {result['skip']}")
        print(f"  失败: {result['error']}")
        print(f"  总计: {result['total']}")
        
        if self.dry_run:
            print("[试运行模式] 未实际执行检查")
            print("如需执行，请设置 dry_run=False")
        else:
            print("✅ 检查完成")
        print("=" * 70)