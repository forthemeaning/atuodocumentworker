# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Batch keyword-search utility for WPS Word documents (.doc/.docx). Used by 川菜人工智能重点实验室 to locate keywords across large collections of documents and export results to Excel.

## Architecture

Two modules:

- **`atuo_check.py`** — Core engine. Uses `win32com.client` to interface with WPS Office COM (`KWPS.Application`). Opens a single Word document, iterates all paragraphs, applies a regex pattern, and returns matching text with page numbers via `Range.Information(3)` (wdActiveEndAdjustedPageNumber). Handles COM resource cleanup in `finally` block.

- **`check_manager.py`** — Batch orchestrator. Reads keywords from an Excel file (first column), recursively discovers Word files in a folder, calls `atuo_check.get_match_pages_com()` for each keyword/file pair, and writes results to an Excel output file.

## Data Flow

```
Excel (.xlsx, column A)
    ──► check_manager.batch_check()
          ──► get_word_files() [recursive os.walk]
                ──► get_match_pages_com() per keyword
                      ──► WPS COM (KWPS.Application)
                          ──► Documents.Open → Paragraphs → Range.Information(3)
    ──► DataFrame → Excel output
```

## Key Dependencies

- `pywin32` — WPS COM interop (`pip install pywin32`)
- `pandas` — Excel read/write (`pip install pandas openpyxl`)
- WPS Office must be installed (uses `KWPS.Application` ProgID, not `Word.Application`)

## Running

Each script has a `__main__` block with hardcoded file paths — edit paths directly then run:

```bash
python atuo_check.py      # single-file search
python check_manager.py   # batch search
```

## Important Notes

- WPS COM is single-threaded — batch search processes files sequentially
- `Range.Information(3)` returns the adjusted page number as WPS paginates the document
- The `finally` block in `get_match_pages_com` always calls `doc.Close()` and `word.Quit()` to prevent orphaned WPS processes
- Regex patterns are Python-flavored, passed directly to `re.finditer`
