# Images to Word Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create a Python CLI script that batch-imports images from a folder into a Word document's single-column table with configurable cell sizes.

**Architecture:** Single-file script (`images_to_word.py`). Use `PIL` to read image dimensions, `python-docx` to create Word doc with table. Each image becomes one row in a single-column table, auto-scaled to fit within cell dimensions while preserving aspect ratio.

**Tech Stack:** Python 3, python-docx, Pillow (PIL)

---

### Task 1: Create the script

**Files:**
- Create: `C:\file\aiwork\newforlder\images_to_word.py`

- [ ] **Step 1: Write the complete script**

```python
#!/usr/bin/env python3
"""Batch import images into a Word document's single-column table."""

import argparse
import os
import sys
from PIL import Image
from docx import Document
from docx.shared import Cm, Emu
from docx.enum.table import WD_ALIGN_VERTICAL


SUPPORTED_EXT = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"}


def parse_args():
    parser = argparse.ArgumentParser(description="Batch import images into Word table")
    parser.add_argument("--folder", required=True, help="Source folder containing images")
    parser.add_argument("--output", default="output.docx", help="Output Word file path")
    parser.add_argument("--width", type=float, default=8.0, help="Column width in cm (default: 8)")
    parser.add_argument("--height", type=float, default=6.0, help="Row height in cm (default: 6)")
    return parser.parse_args()


def get_image_files(folder):
    if not os.path.isdir(folder):
        print(f"Error: folder '{folder}' does not exist.")
        sys.exit(1)
    files = sorted(
        f for f in os.listdir(folder)
        if os.path.splitext(f)[1].lower() in SUPPORTED_EXT
    )
    if not files:
        print(f"Error: no supported image files found in '{folder}'.")
        sys.exit(1)
    return files


def calc_scaled_size(img_path, max_w_emu, max_h_emu):
    """Calculate scaled EMU dimensions preserving aspect ratio."""
    with Image.open(img_path) as img:
        px_w, px_h = img.size
    native_w_emu = int(px_w * 914400 / 72)
    native_h_emu = int(px_h * 914400 / 72)
    scale = min(max_w_emu / native_w_emu, max_h_emu / native_h_emu)
    return int(native_w_emu * scale), int(native_h_emu * scale)


def main():
    args = parse_args()

    cell_width_emu = Cm(args.width).emu
    cell_height_emu = Cm(args.height).emu

    image_files = get_image_files(args.folder)
    doc = Document()

    table = doc.add_table(rows=len(image_files), cols=1)
    table.autofit = False

    for i, filename in enumerate(image_files):
        filepath = os.path.join(args.folder, filename)
        cell = table.rows[i].cells[0]

        table.rows[i].height = Emu(cell_height_emu)
        cell.width = Emu(cell_width_emu)
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        cell.paragraphs[0].clear()

        try:
            margin = 0.95
            img_w_emu, img_h_emu = calc_scaled_size(
                filepath,
                int(cell_width_emu * margin),
                int(cell_height_emu * margin),
            )
        except Exception as e:
            print(f"  Skipping '{filename}': {e}")
            cell.paragraphs[0].text = f"[Error: {filename}]"
            continue

        run = cell.paragraphs[0].add_run()
        run.add_picture(filepath, width=Emu(img_w_emu), height=Emu(img_h_emu))
        print(f"  {filename}")

    doc.save(args.output)
    print(f"\nDone! {len(image_files)} images -> '{args.output}'")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Verify the script runs (syntax check)**

Run: `python -c "import ast; ast.parse(open('C:/file/aiwork/newforlder/images_to_word.py').read()); print('Syntax OK')"`
Expected: `Syntax OK`

- [ ] **Step 3: Functional test with sample images**

```bash
mkdir -p /tmp/test_images
# Create a few test images
python -c "
from PIL import Image
for i, size in enumerate([(100,200), (400,300), (800,600)]):
    img = Image.new('RGB', size, (50*i+50, 50*i+50, 200))
    img.save(f'/tmp/test_images/img{i}_{size[0]}x{size[1]}.png')
"
```

Run: `python C:/file/aiwork/newforlder/images_to_word.py --folder /tmp/test_images --output /tmp/test_output.docx --width 6 --height 4`
Expected: Script completes with "Done! 3 images -> '/tmp/test_output.docx'"

- [ ] **Step 4: Clean up test files**

Run: `rm -rf /tmp/test_images /tmp/test_output.docx`
