# 文件批量重命名工具

## 功能特点

1. **子名连接重命名**：支持多个子名字段，自动跳过空值，灵活连接
2. **自动扫描**：扫描文件夹中的 Word 和 PDF 文件，生成重命名模板
3. **灵活配置**：支持子名1-子名N组合，或手动填写新文件名
4. **增量处理**：只处理填写了配置的文件，未填写的自动跳过
5. **安全试运行**：支持试运行模式，预览重命名结果
6. **连接符配置**：可自定义子名之间的连接符

## 文件结构

```
rename_tool/
├── README.md              # 项目文档
├── USAGE.md              # 使用说明
├── __init__.py           # 包初始化
├── excel_handler.py      # Excel文件处理
├── file_operations.py    # 文件操作
├── file_rename.py        # 主程序接口
├── quick_rename.py       # 快速脚本
├── user_script.py        # 用户脚本
└── rename_logic.py       # 重命名逻辑
```

## 核心功能

### 子名连接功能
- **子名1-子名N**：可填写多个子名字段
- **自动跳过**：空的子名不会被连接
- **原名保持**：如果所有子名都为空，则保持原始文件名
- **灵活连接**：使用连接符将非空子名连接成新文件名

### 示例
```
子名1: 项目
子名2: (空)
子名3: 报告
连接符: _
结果: 项目_报告.docx
```

## 使用方法

### 方法一：快速脚本
```bash
# 1. 修改 quick_rename.py 中的目标路径
FOLDER_PATH = r"你的文件夹路径"

# 2. 运行脚本
python quick_rename.py

# 3. 选择操作：
#    1 - 生成模板
#    2 - 试运行重命名
#    3 - 执行重命名
```

### 方法二：用户脚本
```bash
# 1. 修改 user_script.py 中的目标路径
folder_path = r"你的文件夹路径"

# 2. 运行脚本
python user_script.py

# 3. 按提示选择操作
```

### 方法三：编程接口
```python
from rename_tool import generate_rename_template, batch_rename

# 生成模板
generate_rename_template("文件夹路径", separator="_")

# 批量重命名（试运行）
batch_rename("文件夹路径", "模板路径", dry_run=True)

# 批量重命名（执行）
batch_rename("文件夹路径", "模板路径", dry_run=False)
```

## 使用流程

### 第一步：生成模板
```bash
python quick_rename.py
# 选择 1 - 生成模板
```

或在代码中：
```python
from rename_tool import generate_rename_template

generate_rename_template("你的文件夹路径", separator="_")
```

生成 `rename_template.xlsx`，包含以下列：
- 原文件名
- 子名1
- 子名2
- 子名3
- ...
- 连接符
- 新文件名（可选，手动填写）
- 文件扩展名
- 文件路径

### 第二步：填写配置
打开生成的Excel文件，填写：
- **子名N**：填写子名，空值会被跳过
- **连接符**：默认为"_"，可修改
- **新文件名**：可选，直接填写完整的新文件名

新文件名自动生成规则：`非空子名1 + 连接符 + 非空子名2 + 连接符 + 非空子名3 + ... + 文件扩展名`

### 第三步：执行重命名
```python
from rename_tool import batch_rename

# 试运行（预览结果）
batch_rename("原文件夹", "rename_template.xlsx", dry_run=True)

# 实际执行
batch_rename("原文件夹", "rename_template.xlsx", dry_run=False)
```

## 输出结果

- **result文件夹**：重命名后的文件（在与原文件夹同级的位置）
- **rename_log.xlsx**：重命名记录日志

## 注意事项

1. 原文件不会被修改，而是复制到新文件夹
2. 如果目标文件已存在，会自动跳过
3. 支持增量处理，只处理填写了配置的文件
4. 建议先使用试运行模式预览结果
5. 仅处理 Word (.doc, .docx) 和 PDF (.pdf) 文件
6. 空的子名字段会被跳过，不影响连接结果
7. 所有子名都为空时，文件保持原始名称

## 脚本使用说明

### quick_rename.py
- 简洁版脚本
- 只需修改顶部路径变量
- 适合熟悉流程的用户

### user_script.py
- 交互式界面
- 详细的操作提示
- 适合初学者使用