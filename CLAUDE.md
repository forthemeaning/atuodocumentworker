# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python document processing toolkit with three self-contained tools:
- **rename_tool** — Batch file renaming via Excel templates (copy-based, not move)
- **check_tool** — Regex search in Word documents via WPS COM (Windows-only)
- **sort_tool** — Excel row sorting by reference column order (exact + fuzzy match)

## Running Tools

```bash
# Rename tool (non-recursive, .doc/.docx/.pdf by default)
python rename_tool/file_rename.py     # generate template + batch rename
python rename_tool/quick_rename.py    # edit FOLDER_PATH in script first

# Check tool (recursive, requires WPS on Windows)
python check_tool/check_main.py       # generate config + batch check
python check_tool/quick_check.py      # edit FOLDER_PATH in script first

# Sort tool (exact + fuzzy match)
python sort_tool/sort_main.py         # interactive mode
python sort_tool/user_sort.py         # interactive mode
python sort_tool/quick_sort.py        # edit paths in script first
```

## Running Tests

```bash
# Sort tool tests (the only tool with tests)
cd sort_tool/test
python create_test_files.py           # generate test reference.xlsx + target.xlsx
python test_sort.py                   # run sort test
```

## Architecture

Each tool follows the same structure:
- `*_main.py` — public `generate_*()` + `batch_*()` API functions
- `*_logic.py` / `*_processor.py` — core logic classes
- `excel_handler.py` — pandas wrapper (separate impl per tool, different APIs)
- `file_operations.py` — file I/O utilities
- `quick_*.py` — single-run script (hardcoded paths, edit before run)
- `user_*.py` — interactive CLI script

## Key Patterns

**Dual import strategy**: Modules handle both `python module.py` and `python -m package.module` via try/except:
```python
try:
    from .file_operations import get_files  # package-relative
except ImportError:
    from file_operations import get_files  # direct-run
```

**Naming**: `*_main.py` for public API, `*_logic.py` for logic classes, `user_*.py` for interactive scripts.

**Dry-run**: All batch operations accept `dry_run=True` (default in rename_tool) to preview without side effects.

**Error handling**: Console `print()`-based throughout — no logging framework.

## Cross-Tool Differences

| Aspect | rename_tool | check_tool | sort_tool |
|--------|-------------|------------|-----------|
| File scan | Non-recursive (`os.listdir`) | Recursive (`os.walk`) | N/A (Excel input) |
| Default extensions | `.doc`, `.docx`, `.pdf` | `.docx`, `.doc` | `.xlsx` |
| File operation | Copy (`shutil.copy2`) | Read-only (regex scan) | Read-only (sort + write) |
| ExcelHandler API | `read_excel(path)` / `write_excel(data, path, index)` / `filter_valid_rows(df, columns)` | `read_excel(path)` / `write_excel(data, path, columns)` / `filter_valid_rows(df, columns)` | `read_excel(path)` / `write_excel(df, path)` / `get_columns(path)` / `get_column_values(df, col)` |
| COM dependency | None | `win32com.client` → `KWPS.Application` | None |

The `excel_handler.py` in each tool evolved independently — **do not assume API compatibility** between them.

## Dependencies

- `pandas`, `openpyxl` (Excel I/O across all tools)
- `pywin32` / `win32com.client` (WPS COM, check_tool only — lazy-imported, optional)
- Python 3.10+
- No `requirements.txt` — install manually or pin per tool
