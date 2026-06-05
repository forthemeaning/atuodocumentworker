import os
import sys
import json
import uuid
import shutil
import tempfile
import string
import traceback
import io
import contextlib

import pandas as pd
from flask import Flask, render_template, request, jsonify, send_file

# Add project root to path
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# Import existing tool modules
from rename_tool.file_operations import get_files as rename_get_files
from rename_tool.file_operations import file_exists, folder_exists
from rename_tool.rename_logic import BatchRenamer

from check_tool.file_operations import get_files as check_get_files
from check_tool.check_processor import check_win32com_availability, get_match_pages_com

from sort_tool.excel_handler import ExcelHandler as SortExcelHandler
from sort_tool.sort_logic import SortLogic

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload

# In-memory store for downloadable results
_download_store = {}


# ============================================================
#  Directory / File Explorer
# ============================================================

@app.route('/api/explorer/list', methods=['POST'])
def explorer_list():
    """List contents of a directory for the browser file picker."""
    data = request.get_json(force=True)
    path = data.get('path', '').strip()

    # Root level: list drives on Windows
    if not path:
        drives = []
        for letter in string.ascii_uppercase:
            drive = f'{letter}:\\'
            if os.path.exists(drive):
                try:
                    label = f'{letter}:'
                    drives.append({'name': label, 'path': drive, 'type': 'drive'})
                except Exception:
                    pass
        return jsonify({'path': '', 'items': drives, 'type': 'drives', 'parent': None})

    path = os.path.normpath(path)

    if not os.path.exists(path):
        return jsonify({'error': '路径不存在'}), 404

    if os.path.isfile(path):
        parent = os.path.dirname(path)
        return jsonify({'path': path, 'type': 'file', 'parent': parent,
                        'name': os.path.basename(path)})

    # Directory listing
    items = []
    try:
        entries = os.listdir(path)
    except PermissionError:
        entries = []

    # Add parent directory entry
    parent_dir = os.path.dirname(path.rstrip('\\').rstrip('/'))
    if parent_dir and parent_dir != path:
        items.append({'name': '..', 'path': parent_dir, 'type': 'parent'})

    # Sort: directories first, then files, alphabetically
    dirs = []
    files = []
    for entry in sorted(entries, key=str.lower):
        full = os.path.join(path, entry)
        try:
            if os.path.isdir(full):
                dirs.append({'name': entry, 'path': full, 'type': 'dir'})
            else:
                ext = os.path.splitext(entry)[1].lower()
                files.append({'name': entry, 'path': full, 'type': 'file', 'ext': ext})
        except (OSError, PermissionError):
            pass
    items.extend(dirs)
    items.extend(files)

    return jsonify({'path': path, 'items': items, 'type': 'dir', 'parent': parent_dir})


# ============================================================
#  Rename Tool APIs
# ============================================================

@app.route('/api/rename/scan', methods=['POST'])
def rename_scan():
    """Scan a folder and return list of supported files."""
    data = request.get_json(force=True)
    folder_path = data.get('folder_path', '').strip()

    if not folder_path or not os.path.isdir(folder_path):
        return jsonify({'error': '文件夹不存在或路径无效'}), 400

    try:
        files = rename_get_files(folder_path)
    except Exception as e:
        return jsonify({'error': f'扫描文件夹失败: {str(e)}'}), 500

    file_list = []
    for f in files:
        name = os.path.basename(f)
        ext = os.path.splitext(name)[1].lower()
        try:
            size = os.path.getsize(f)
        except OSError:
            size = 0
        try:
            mtime = os.path.getmtime(f)
        except OSError:
            mtime = 0

        file_list.append({
            'name': name,
            'path': f,
            'ext': ext,
            'size': size,
            'modified': mtime,
        })

    return jsonify({'folder_path': folder_path, 'files': file_list, 'count': len(file_list)})


@app.route('/api/rename/execute', methods=['POST'])
def rename_execute():
    """Execute batch rename (copy-based, output to result/ subfolder)."""
    data = request.get_json(force=True)
    folder_path = data.get('folder_path', '').strip()
    rules = data.get('rules', [])
    dry_run = data.get('dry_run', True)

    if not folder_path or not os.path.isdir(folder_path):
        return jsonify({'error': '文件夹不存在或路径无效'}), 400

    output_folder = os.path.join(_project_root, 'rename_tool', 'result')
    results = []
    success = skip = error = 0

    for rule in rules:
        original = rule.get('original', '')
        new_name = rule.get('new_name', '').strip()

        if not new_name:
            skip += 1
            results.append({'original': original, 'new_name': '', 'status': 'skip', 'message': '新文件名为空'})
            continue

        src = os.path.join(folder_path, original)
        dst = os.path.join(output_folder, new_name)

        if not os.path.isfile(src):
            error += 1
            results.append({'original': original, 'new_name': new_name, 'status': 'error', 'message': '源文件不存在'})
            continue

        if os.path.exists(dst):
            skip += 1
            results.append({'original': original, 'new_name': new_name, 'status': 'skip', 'message': '目标文件已存在'})
            continue

        if not dry_run:
            try:
                os.makedirs(output_folder, exist_ok=True)
                shutil.copy2(src, dst)
                success += 1
                results.append({'original': original, 'new_name': new_name, 'status': 'success'})
            except Exception as e:
                error += 1
                results.append({'original': original, 'new_name': new_name, 'status': 'error', 'message': str(e)})
        else:
            success += 1
            results.append({'original': original, 'new_name': new_name, 'status': 'preview-ok'})

    return jsonify({
        'success': success,
        'skip': skip,
        'error': error,
        'total': len(rules),
        'details': results,
        'output_folder': output_folder,
        'dry_run': dry_run,
    })


# ============================================================
#  Check Tool APIs
# ============================================================

@app.route('/api/check/scan', methods=['POST'])
def check_scan():
    """Scan folder for Word documents."""
    data = request.get_json(force=True)
    folder_path = data.get('folder_path', '').strip()

    if not folder_path or not os.path.isdir(folder_path):
        return jsonify({'error': '文件夹不存在或路径无效'}), 400

    try:
        files = check_get_files(folder_path, ['.docx', '.doc'])
    except Exception as e:
        return jsonify({'error': f'扫描文件夹失败: {str(e)}'}), 500

    file_list = []
    for f in files:
        file_list.append({
            'name': os.path.basename(f),
            'path': f,
        })

    com_available = check_win32com_availability()

    return jsonify({
        'folder_path': folder_path,
        'files': file_list,
        'count': len(file_list),
        'com_available': com_available,
    })


@app.route('/api/check/execute', methods=['POST'])
def check_execute():
    """Execute regex check on Word documents."""
    data = request.get_json(force=True)
    folder_path = data.get('folder_path', '').strip()
    patterns = data.get('patterns', {})  # dict: {filename: regex}

    if not folder_path or not os.path.isdir(folder_path):
        return jsonify({'error': '文件夹不存在或路径无效'}), 400

    if not check_win32com_availability():
        return jsonify({'error': 'win32com 不可用，检查工具需要 WPS 或 Microsoft Word COM 接口'}), 503

    try:
        word_files = check_get_files(folder_path, ['.docx', '.doc'])

        if not word_files:
            return jsonify({'error': '未找到Word文档(.docx/.doc)'}), 404

        all_results = []
        success = skip = error = 0
        debug_log = []

        for file_path in word_files:
            file_name = os.path.basename(file_path)
            regex = patterns.get(file_name, '')

            if not regex:
                skip += 1
                continue

            debug_log.append(f'检查: {file_name} -> regex: {regex}')

            try:
                # Capture stdout from get_match_pages_com
                stdout_capture = io.StringIO()
                with contextlib.redirect_stdout(stdout_capture):
                    matches = get_match_pages_com(file_path, regex)
                com_output = stdout_capture.getvalue().strip()
                if com_output:
                    for line in com_output.split('\n'):
                        debug_log.append(f'  [COM] {line}')
                debug_log.append(f'  结果: {len(matches)} 条匹配')
                for m in matches:
                    all_results.append({
                        'file': file_name,
                        'text': m.get('text', ''),
                        'page': m.get('page', ''),
                    })
                if matches:
                    success += 1
                else:
                    skip += 1
                    debug_log.append(f'  跳过: 无匹配')
            except Exception as e:
                error += 1
                debug_log.append(f'  错误: {str(e)}')
                all_results.append({
                    'file': file_name,
                    'text': f'[错误] {str(e)}',
                    'page': '',
                })

        # Save results to check_tool/result/
        check_result_folder = os.path.join(_project_root, 'check_tool', 'result')
        os.makedirs(check_result_folder, exist_ok=True)
        result_path = os.path.join(check_result_folder, 'check_result.xlsx')
        if all_results:
            result_df = pd.DataFrame(all_results)
        else:
            result_df = pd.DataFrame([{'file': '', 'text': '无匹配结果', 'page': ''}])
        result_df.to_excel(result_path, index=False)

        return jsonify({
            'results': all_results,
            'stats': {'success': success, 'skip': skip, 'error': error, 'total': len(word_files)},
            'debug': debug_log,
            'saved_to': result_path,
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'检查失败: {str(e)}'}), 500


# ============================================================
#  Sort Tool APIs
# ============================================================

@app.route('/api/sort/columns', methods=['POST'])
def sort_columns():
    """Get column names from an Excel file."""
    data = request.get_json(force=True)
    file_path = data.get('file_path', '').strip()

    if not file_path or not os.path.isfile(file_path):
        return jsonify({'error': '文件不存在或路径无效'}), 400

    try:
        columns = SortExcelHandler.get_columns(file_path)
        if not columns:
            return jsonify({'error': '无法读取文件列名'}), 400
        return jsonify({'columns': columns, 'file_path': file_path})
    except Exception as e:
        return jsonify({'error': f'读取列名失败: {str(e)}'}), 500


@app.route('/api/sort/preview', methods=['POST'])
def sort_preview():
    """Show reference values and target file preview."""
    data = request.get_json(force=True)
    ref_file = data.get('ref_file', '').strip()
    target_file = data.get('target_file', '').strip()
    ref_column = data.get('ref_column', '')

    if not os.path.isfile(ref_file):
        return jsonify({'error': '参照文件不存在'}), 400
    if not os.path.isfile(target_file):
        return jsonify({'error': '目标文件不存在'}), 400

    try:
        ref_df = SortExcelHandler.read_excel(ref_file)
        target_df = SortExcelHandler.read_excel(target_file)

        ref_values = SortExcelHandler.get_column_values(ref_df, ref_column)
        target_preview = target_df.head(10).to_dict(orient='records')

        return jsonify({
            'ref_values_count': len(ref_values),
            'ref_values': ref_values[:50],
            'target_preview': target_preview,
            'target_columns': target_df.columns.tolist(),
            'target_rows': len(target_df),
        })
    except Exception as e:
        return jsonify({'error': f'预览失败: {str(e)}'}), 500


@app.route('/api/sort/execute', methods=['POST'])
def sort_execute():
    """Execute sort and return results."""
    data = request.get_json(force=True)
    ref_file = data.get('ref_file', '').strip()
    target_file = data.get('target_file', '').strip()
    ref_column = data.get('ref_column', '')
    match_column = data.get('match_column', '')
    fuzzy = data.get('fuzzy', False)
    keep_unmatched = data.get('keep_unmatched', True)

    if not os.path.isfile(ref_file):
        return jsonify({'error': '参照文件不存在'}), 400
    if not os.path.isfile(target_file):
        return jsonify({'error': '目标文件不存在'}), 400

    try:
        ref_df = SortExcelHandler.read_excel(ref_file)
        target_df = SortExcelHandler.read_excel(target_file)

        ref_values = SortExcelHandler.get_column_values(ref_df, ref_column)

        if fuzzy:
            sorted_df = SortLogic.fuzzy_sort_by_reference(
                target_df, ref_values, match_column, keep_unmatched
            )
        else:
            sorted_df = SortLogic.sort_by_reference(
                target_df, ref_values, match_column, keep_unmatched
            )

        # Save to sort_tool/result for download
        result_folder = os.path.join(_project_root, 'sort_tool', 'result')
        os.makedirs(result_folder, exist_ok=True)
        result_id = str(uuid.uuid4())
        tmp_path = os.path.join(result_folder, f'sorted_{result_id}.xlsx')
        sorted_df.to_excel(tmp_path, index=False)
        _download_store[result_id] = tmp_path

        result_data = sorted_df.to_dict(orient='records')
        # Truncate preview to 200 rows for JSON response
        preview_data = result_data[:200]

        return jsonify({
            'result_id': result_id,
            'columns': sorted_df.columns.tolist(),
            'data': preview_data,
            'total_rows': len(result_data),
            'truncated': len(result_data) > 200,
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'排序失败: {str(e)}'}), 500


@app.route('/api/sort/download/<result_id>')
def sort_download(result_id):
    """Download sorted result as Excel file."""
    if result_id not in _download_store:
        return jsonify({'error': '结果不存在或已过期'}), 404

    filepath = _download_store[result_id]
    if not os.path.isfile(filepath):
        return jsonify({'error': '文件不存在'}), 404

    return send_file(filepath, as_attachment=True, download_name='sorted_result.xlsx',
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


# ============================================================
#  Main
# ============================================================

@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    print('=' * 60)
    print('  文档处理工具 Web 服务')
    print('  访问地址: http://127.0.0.1:5000')
    print('=' * 60)
    app.run(host='127.0.0.1', port=5000, debug=False)
