---
name: excel-analyzer
description: >
  分析Excel文件(.xlsx/.xls)内容的工具，提取所有工作表和表格数据。
  支持显示工作表结构、列名、数据内容，并保存为纯文本格式。
  适用场景：CAN协议Excel文档分析、数据表格提取、技术文档内容查看。
  当用户提到 "分析Excel"、"读取Excel"、"提取Excel表格"、
  "Excel内容提取"、"查看Excel数据"、"协议表格分析" 等关键词时，必须使用本 skill。
---

# Excel文件分析工具 (Excel Analyzer)

## 任务概述

从Excel文件(.xlsx)中提取所有工作表和表格数据，显示工作表结构并保存为纯文本格式。
按照工作表顺序输出，包含完整的列名和数据内容。

**主要功能:**
- ✅ 读取所有工作表
- ✅ 显示工作表结构（行数、列数、列名）
- ✅ 提取完整表格数据
- ✅ 支持中文和特殊字符
- ✅ 彩色控制台输出（前10行预览）
- ✅ 完整数据保存到文本文件

**适用场景:**
- CAN通信协议Excel文档分析
- 数据表格内容提取
- Excel文档结构查看
- 协议数据预处理

---

## 第一步：环境准备

### 1.1 检查Python环境

需要Python 3.8或更高版本：

```bash
python --version
```

### 1.2 验证uv工具

本工具使用uv管理依赖：

```bash
uv --version
```

### 1.3 所需依赖

本Skill依赖以下Python包（已在`pyproject.toml`中定义）：

| 包名 | 版本 | 用途 |
|------|------|------|
| pandas | >=2.0.0 | Excel文件读取和数据处理 |
| openpyxl | >=3.1.0 | Excel文件格式支持 |
| rich | >=13.0.0 | 彩色控制台输出 |

---

## 第二步：输入文件准备

### 2.1 支持的文件格式

| 格式 | 扩展名 | 是否支持 |
|------|--------|---------|
| Excel 2007+ | `.xlsx` | ✅ 是 |
| Excel 97-2003 | `.xls` | ✅ 是（需xlrd） |

### 2.2 文件位置

- 可以是本地文件的绝对路径
- 可以是相对路径
- 支持包含中文的路径

### 2.3 文件要求

- 文件必须存在且可读
- 文件内容应为有效的Excel格式
- 支持多个工作表

---

## 第三步：分析Excel文件

### 3.1 基本用法

```bash
# 分析Excel文件（默认输出同名.txt）
uv run python .github/skills/excel-analyzer/scripts/analyze_excel.py protocol.xlsx

# 指定输出文件
uv run python .github/skills/excel-analyzer/scripts/analyze_excel.py protocol.xlsx -o analysis.txt

# 使用完整路径
uv run python .github/skills/excel-analyzer/scripts/analyze_excel.py "d:\path\to\file.xlsx" -o outputs\result.txt
```

### 3.2 命令参数

| 参数 | 简写 | 必需 | 说明 | 示例 |
|------|------|------|------|------|
| excel_file | - | ✅ | 输入的Excel文件路径 | `protocol.xlsx` |
| --output | -o | ❌ | 输出文本文件路径（默认：同名.txt） | `-o result.txt` |

### 3.3 输出格式

提取的文本文件结构如下：

```
Excel文件: protocol.xlsx
================================================================================

================================================================================
工作表 1: Sheet1
行数: 31, 列数: 9
================================================================================

列名: 列1, 列2, 列3, ...

数据内容:
--------------------------------------------------------------------------------
列1 | 列2 | 列3 | ...
--------------------------------------------------------------------------------
行1: 数据1 | 数据2 | 数据3 | ...
行2: 数据1 | 数据2 | 数据3 | ...
...
```

### 3.4 控制台输出

运行时会在控制台显示：
- 文件打开状态
- 工作表数量
- 每个工作表的基本信息
- 前10行数据预览（彩色表格）

---

## 第四步：验证输出结果

### 4.1 检查输出文件

```bash
# Windows
type output.txt

# 查看文件大小
dir output.txt
```

### 4.2 控制台信息

运行脚本后会显示：

```
✓ Excel文件打开成功: protocol.xlsx
工作表数量: 2

工作表 1: Sheet1
  行数: 31, 列数: 9
  列名: No, Start bit, Length(Bit), ...

[彩色表格显示前10行数据]

✓ 分析完成！
✓ 结果已保存到: protocol.txt
```

---

## 完整使用示例

### 示例1：分析CAN协议Excel文件

```bash
# 分析PDU通讯协议Excel文件
uv run python .github/skills/excel-analyzer/scripts/analyze_excel.py \
  "d:\weixin\PDU_通讯协议.xlsx" \
  -o outputs\PDU_analysis.txt
```

**预期输出:**
```
✓ Excel文件打开成功: PDU_通讯协议.xlsx
工作表数量: 1

工作表 1: Sheet1
  行数: 31, 列数: 9
  列名: 4.5 VCU_COMMAND, Unnamed: 1, ...

✓ 分析完成！
✓ 结果已保存到: outputs\PDU_analysis.txt
```

### 示例2：分析多工作表Excel

```bash
# 分析包含多个工作表的文件
uv run python .github/skills/excel-analyzer/scripts/analyze_excel.py \
  complex_data.xlsx \
  -o analysis_result.txt
```

### 示例3：用于协议转换前的预处理

```bash
# 第1步：分析Excel文件
uv run python .github/skills/excel-analyzer/scripts/analyze_excel.py \
  protocol.xlsx -o protocol_analysis.txt

# 第2步：查看分析结果，了解表格结构
type protocol_analysis.txt

# 第3步：根据结构手动或自动生成Unified CSV
# ...

# 第4步：转换为DBC
uv run python .github/skills/csv-to-dbc/scripts/csv2dbc.py \
  convert protocol.csv -o protocol.dbc
```

---

## 命令参数详解

### analyze_excel.py

```
用法: analyze_excel.py [-h] [-o OUTPUT] excel_file

分析Excel文件内容

位置参数:
  excel_file            要分析的Excel文件路径

可选参数:
  -h, --help            显示帮助信息并退出
  -o OUTPUT, --output OUTPUT
                        输出文本文件路径（可选）

示例:
  # 分析Excel文件
  python analyze_excel.py protocol.xlsx
  
  # 保存分析结果
  python analyze_excel.py protocol.xlsx -o analysis.txt
  
  # 使用uv运行
  uv run python analyze_excel.py protocol.xlsx -o analysis.txt
```

---

## 功能特性

### 核心特性

- ✅ **多工作表支持**: 自动读取所有工作表
- ✅ **完整数据提取**: 提取所有行列数据
- ✅ **结构分析**: 显示行数、列数、列名
- ✅ **编码支持**: 完整支持UTF-8，正确处理中文
- ✅ **彩色预览**: 使用Rich库显示前10行数据
- ✅ **全量保存**: 完整数据保存到文本文件

### 输出特性

- ✅ **分隔符清晰**: 使用 `|` 分隔列数据
- ✅ **行号标记**: 每行带行号标识
- ✅ **空值处理**: 自动处理NaN和空值
- ✅ **工作表分隔**: 清晰的工作表边界标记

### 错误处理

- ✅ **文件验证**: 检查文件是否存在
- ✅ **格式验证**: 验证Excel文件格式
- ✅ **异常捕获**: 捕获并显示有意义的错误信息
- ✅ **退出码**: 正确返回0(成功)或1(失败)

---

## 依赖

### Python包依赖

```toml
[project]
name = "excel-analyzer"
version = "1.0.0"
description = "Analyze Excel files and extract table content"
requires-python = ">=3.8"
dependencies = [
    "pandas>=2.0.0",
    "openpyxl>=3.1.0",
    "rich>=13.0.0",
]
```

### 系统依赖

- Python 3.8+
- uv (包管理器)
- Windows / Linux / macOS

---

## 故障排除

### 问题1: 无法打开Excel文件

**错误信息:**
```
❌ 无法打开Excel文件: [Errno 2] No such file or directory
```

**解决方案:**
- 检查文件路径是否正确
- 确认文件确实存在
- 使用绝对路径而非相对路径
- 检查路径中的中文字符是否正确

### 问题2: 缺少依赖

**错误信息:**
```
ModuleNotFoundError: No module named 'pandas'
```

**解决方案:**
```bash
# 使用uv同步依赖
uv sync

# 或手动安装
pip install pandas openpyxl rich
```

### 问题3: 读取.xls文件失败

**错误信息:**
```
ImportError: Missing optional dependency 'xlrd'
```

**解决方案:**
```bash
# 安装xlrd支持.xls格式
pip install xlrd
```

### 问题4: 编码错误

**错误信息:**
```
UnicodeDecodeError: 'charmap' codec can't decode characters
```

**解决方案:**
- 确保输出文件使用UTF-8编码
- 脚本已默认使用UTF-8
- 检查终端编码设置

### 问题5: 数据显示不完整

**症状:** 某些列数据被截断

**解决方案:**
- 控制台预览只显示前10行
- 完整数据保存在输出文件中
- 使用文本编辑器查看完整输出文件

---

## 最佳实践

### 1. 文件组织

```
project/
├── inputs/          # 输入的Excel文件
│   ├── protocol1.xlsx
│   └── protocol2.xlsx
└── outputs/         # 分析结果文本文件
    ├── protocol1_analysis.txt
    └── protocol2_analysis.txt
```

### 2. 命名规范

- 使用有意义的输出文件名
- 添加 `_analysis` 后缀便于识别
- 保持输入输出文件名关联

### 3. 批量处理

创建批处理脚本：

```powershell
# batch_analyze.ps1
$inputDir = "inputs"
$outputDir = "outputs"

New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

Get-ChildItem "$inputDir\*.xlsx" | ForEach-Object {
    $outputFile = "$outputDir\$($_.BaseName)_analysis.txt"
    Write-Host "分析: $($_.Name)" -ForegroundColor Cyan
    uv run python .github/skills/excel-analyzer/scripts/analyze_excel.py $_.FullName -o $outputFile
}
```

### 4. 后续处理

分析结果可用于：
- 理解Excel表格结构
- 准备协议数据转换
- 数据提取和预处理
- 表格内容验证

---

## 输出数据结构

### 工作表信息

每个工作表包含：
- 工作表名称
- 行数和列数
- 列名列表
- 完整数据内容

### 数据格式

```
行号: 列1数据 | 列2数据 | 列3数据 | ...
```

### 空值处理

- NaN值显示为空字符串
- None值显示为空字符串
- 数值自动转换为字符串

---

## 相关 Skills

- **docx-extractor**: 提取Word文档内容
- **pdf-summary**: 提取PDF文档内容
- **csv-to-dbc**: 将CSV转换为DBC文件
- **pdf-to-can-csv**: 将协议文档转换为CSV

---

## 参考资源

- [pandas 官方文档](https://pandas.pydata.org/docs/)
- [openpyxl 文档](https://openpyxl.readthedocs.io/)
- [Rich 库文档](https://rich.readthedocs.io/)

---

## 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0.0 | 2026-03-11 | 初始版本，支持Excel文件分析和数据提取 |
