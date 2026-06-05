---
name: images-to-word
description: Python script to batch import images into a Word document's single-column table with configurable cell sizes
---

# Images to Word - Design Spec

## Overview
A Python CLI script that batch-imports images from a folder into a new Word document. Images are placed in a single-column table, each image occupying one row, auto-scaled to fit within the configured cell dimensions while preserving aspect ratio.

## Usage
```
python images_to_word.py --folder ./images --output output.docx --width 8 --height 6
```

### Parameters
| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `--folder` | Yes | — | Source folder containing images |
| `--output` | No | `output.docx` | Output Word file path |
| `--width` | No | 8 | Column width in cm |
| `--height` | No | 6 | Row height in cm |

## Architecture
Single-file script (`images_to_word.py`), no classes needed.

### Data Flow
1. Parse CLI args → source folder + options
2. Scan folder → filter image files by extension
3. Sort files → consistent ordering
4. Create Word doc + single-column table
5. For each image → open via PIL, scale to fit cell, insert into cell
6. Save doc

### Supported Image Formats
`.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`

### Image Scaling Logic
- Calculate scale factor: `min(cell_width / img_width, cell_height / img_height)`
- Apply scale to both dimensions (maintain aspect ratio)
- Insert scaled image centered in cell

### Error Handling
- Skip unreadable/corrupt images with warning
- Clear error if folder is empty or doesn't exist
- Inform user of total imported count

## Dependencies
- `python-docx` — Word document creation
- `PIL/Pillow` — image dimension reading + scaling

## Out of Scope
- Multi-column layouts
- Custom image ordering (always alphabetical by filename)
- Image captions or metadata
- GUI interface
