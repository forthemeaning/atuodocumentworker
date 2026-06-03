# 文档内容检查工具

## 功能特点

1. **配置化检查**：支持为不同文件配置不同的正则表达式
2. **自动扫描**：扫描文件夹中的 Word 文件，生成配置模板
3. **批量处理**：根据配置模板批量检查文档内容
4. **增量处理**：只处理有配置的文件，未配置的自动跳过
5. **安全试运行**：支持试运行模式，预览检查结果
6. **页码定位**：精确定位匹配内容所在的页码

## 文件结构

```
check_tool/
├── README.md              # 项目文档
├── __init__.py           # 包初始化
├── check_main.py         # 主程序接口
├── check_processor.py    # 检查逻辑处理
├── excel_handler.py      # Excel文件处理
├── file_operations.py    # 文件操作
├── quick_check.py        # 快速脚本
└── user_check.py         # 用户脚本
```

## 核心功能

### 配置化检查
- **文件名匹配**：根据文件名匹配对应的正则规则
- **正则表达式**：为每个文件配置特定的搜索模式
- **页码定位**：返回匹配内容所在的页码

## 使用方法

### 方法一：快速脚本
```bash
# 1. 修改 quick_check.py 中的目标路径
FOLDER_PATH = r"你的文件夹路径"

# 2. 运行脚本
python quick_check.py

# 3. 选择操作：
#    1 - 生成配置
#    2 - 试运行检查
#    3 - 执行检查
```

### 方法二：用户脚本
```bash
# 1. 修改 user_check.py 中的目标路径
folder_path = r"你的文件夹路径"

# 2. 运行脚本
python user_check.py

# 3. 按提示选择操作
```

### 方法三：编程接口
```python
from check_tool import generate_config_template, batch_check

# 生成配置
generate_config_template("文件夹路径", pattern="")

# 批量检查（试运行）
batch_check("文件夹路径", "配置路径", dry_run=True)

# 批量检查（执行）
batch_check("文件夹路径", "配置路径", dry_run=False)
```

## 使用流程

### 第一步：生成配置
```bash
python quick_check.py
# 选择 1 - 生成配置
```

或在代码中：
```python
from check_tool import generate_config_template

generate_config_template("你的文件夹路径", pattern="")
```

生成 `config_template.xlsx`，包含以下列：
- 原文件名
- 文件路径
- 正则表达式（需手动填写）
- 文件扩展名

### 第二步：填写配置
打开生成的Excel文件，在"正则表达式"列中填写对应的搜索模式。

### 第三步：执行检查
```python
from check_tool import batch_check

# 试运行（预览结果）
batch_check("原文件夹", "config_template.xlsx", dry_run=True)

# 实际执行
batch_check("原文件夹", "config_template.xlsx", dry_run=False)
```

## 输出结果

- **checked文件夹**：检查结果文件夹
- **check_result.xlsx**：检查结果日志

## 注意事项

1. 仅处理 Word (.doc, .docx) 文件
2. 支持增量处理，只处理有配置的文件
3. 建议先使用试运行模式预览结果
4. 需要安装 WPS 或 Word 并启用 COM 接口
5. 正则表达式支持复杂模式匹配
6. 页码定位精确到段落级别