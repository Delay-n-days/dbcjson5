---
name: pdf-summary
description: >
  提取并总结 CAN 通讯协议 PDF 文档。
  支持完整的文本提取、统计分析、关键词搜索。
  使用 Typer 框架实现的现代化 CLI 工具。
  备选方案：若 summarize_pdf.py 无法读取 PDF，使用 extract_pdf.py 提取完整的 PDF 文本和表格。
  适用场景：用户需要提取 PDF 中的协议信息、报文定义、信号参数等内容，或从 PDF 中提取内容用于大模型处理生成 CSV。
  当用户提到 "提取PDF"、"总结协议"、"PDF转文本"、"协议文档摘要"、
  "CAN协议提取"、"电机控制器协议"、"通讯协议分析"、"PDF文本提取"、等关键词时，必须使用本 skill。
---

# PDF 提取和总结 Skill

## 任务概述

使用内置的 Typer CLI 工具提取并分析 PDF 文档：

- **`summarize_pdf.py`** - 提取和总结 PDF 文档内容、统计分析、关键词搜索
- **`extract_pdf.py`** - 备选工具，直接提取 PDF 完整文本和表格，供大模型处理

**不要自己编写 PDF 解析脚本**，直接使用内置工具。

---

## 快速开始

### 环境准备（一次性）

```bash
# 1. 安装 uv（如未安装）
python -m pip install uv

# 2. 在项目根目录同步依赖
cd C:\Users\25156\Desktop\dbcjson5
uv sync
```

---

## Tool 1: extract_pdf.py（Typer CLI）

**用途**：直接提取 PDF 文本和表格内容，适合 PDF 无法正常读取或需要完整内容供大模型处理时使用。

### 查看帮助

```bash
cd C:\Users\25156\Desktop\dbcjson5
uv run python ".github/skills/pdf-summary/scripts/extract_pdf.py" --help
```

### 使用示例

#### 1. 基础用法 - 提取并显示内容

```bash
# 自动查找当前目录的 PDF 文件
uv run python ".github/skills/pdf-summary/scripts/extract_pdf.py"

# 指定具体的 PDF 文件
uv run python ".github/skills/pdf-summary/scripts/extract_pdf.py" "绿控传动TMCU通讯协议1C.pdf"
```

#### 2. 提取并保存到文件

```bash
# 保存提取结果到文件（包含完整内容和统计）
uv run python ".github/skills/pdf-summary/scripts/extract_pdf.py" "协议.pdf" \
  --output outputs/pdf_content.txt

# 只保存统计信息，隐藏内容
uv run python ".github/skills/pdf-summary/scripts/extract_pdf.py" "协议.pdf" \
  --output outputs/stats.txt \
  --no-content
```

#### 3. 只显示统计信息（不显示全部内容）

```bash
uv run python ".github/skills/pdf-summary/scripts/extract_pdf.py" "协议.pdf" --no-content
```

### 命令参数

```
用法: extract_pdf.py [OPTIONS] [PDF_PATH]

参数：
  PDF_PATH    PDF 文件路径（可选，自动查找第一个 PDF 文件）

选项：
  --output, -o TEXT    输出文件路径（可选，不指定则仅输出到终端）
  --no-content         隐藏完整文档内容，仅显示统计信息
  --no-stats           隐藏统计信息
  --help               显示帮助信息
```

### 典型输出示例

```
OK PDF 打开成功，共 24 页

======================================================================
第 1 页
======================================================================

【文本内容】
绿控传动 TMCU 通讯协议 1C
版本 修改日期 修改内容 修改者 审核
...

【找到 1 个表格】

--- 表格 1 ---
行 1: ['版本', '修改日期', '修改内容', '修改者', '审核']
行 2: ['V0.2', '2014-6-8', '修改 ...']
...

======================================================================
提取统计
======================================================================
总页数: 24
总文本字符数: 45000
总表格数: 15
```

---

## Tool 2: summarize_pdf.py（Typer CLI）

**用途**：提取、总结 PDF 文档内容，支持关键词搜索和统计分析。

### 查看帮助

```bash
cd C:\Users\25156\Desktop\dbcjson5
uv run python ".github/skills/pdf-summary/scripts/summarize_pdf.py" --help
```

### 使用示例

#### 1. 基础用法 - 显示完整内容和统计

```bash
uv run python ".github/skills/pdf-summary/scripts/summarize_pdf.py" summarize "协议.pdf"
```

#### 2. 只显示统计信息

```bash
uv run python ".github/skills/pdf-summary/scripts/summarize_pdf.py" summarize "协议.pdf" --no-content
```

#### 3. 只显示内容，隐藏统计

```bash
uv run python ".github/skills/pdf-summary/scripts/summarize_pdf.py" summarize "协议.pdf" --no-stats
```

#### 4. 保存到文件

```bash
uv run python ".github/skills/pdf-summary/scripts/summarize_pdf.py" summarize "协议.pdf" \
  --output outputs/summary.txt
```

#### 5. 搜索自定义关键词

```bash
# 搜索多个关键词（逗号分隔）
uv run python ".github/skills/pdf-summary/scripts/summarize_pdf.py" summarize "协议.pdf" \
  --keywords "报文,信号,转矩,波特率"
```

#### 6. 综合用法

```bash
# 搜索关键词，只显示统计，保存结果
uv run python ".github/skills/pdf-summary/scripts/summarize_pdf.py" summarize "协议.pdf" \
  --no-content \
  --keywords "电机,转速,扭矩,电流,温度" \
  --output outputs/keyword_analysis.txt
```

### 命令参数

```
用法: summarize_pdf.py summarize [OPTIONS] PDF_PATH

参数：
  PDF_PATH                PDF 文件路径

选项：
  --output, -o TEXT       输出文件路径（可选）
  --content/--no-content  显示/隐藏完整内容（默认：显示）
  --stats/--no-stats      显示/隐藏统计信息（默认：显示）
  --keywords, -k TEXT     搜索关键词，用逗号分隔（可选）
  --help                  显示帮助信息
```

---

## 第一步：环境准备

### 1.1 确认输入文件

| 文件 | 来源 | 说明 |
|------|------|------|
| `*.pdf` | `C:\Users\25156\Desktop\dbcjson5\` | 输入 PDF 文件（必须） |
| `extract_pdf.py` | **本 skill 内置** `.github/skills/pdf-summary/scripts/` | CLI 脚本（无需用户上传） |
| `summarize_pdf.py` | **本 skill 内置** `.github/skills/pdf-summary/scripts/` | CLI 脚本（无需用户上传） |
| `pyproject.toml` | **本 skill 内置** `.github/skills/pdf-summary/scripts/` | 依赖配置（无需用户上传） |

### 1.2 参照 uv-project-runner skill 完成 uv 安装

```bash
# 检测 uv
uv --version

# 若未安装，执行自动安装
python -m pip install uv
```

---

## 第二步：建立工作目录

```bash
# 创建输出目录
mkdir -p C:\Users\25156\Desktop\dbcjson5\outputs

# 进入项目目录
cd C:\Users\25156\Desktop\dbcjson5

# 同步依赖（使用 uv）
uv sync

# 验证依赖安装
uv run python -c "import pdfplumber, typer; print('OK')"
```

---

## 第三步：运行工具处理 PDF

### 选择工具

| 工具 | 适用场景 | 命令 |
|------|--------|------|
| **extract_pdf.py** | 完整提取所有文本/表格，供大模型处理 | `uv run python ".github/skills/pdf-summary/scripts/extract_pdf.py" "PDF文件名" --output outputs/extracted.txt` |
| **summarize_pdf.py** | 提取+统计+关键词搜索 | `uv run python ".github/skills/pdf-summary/scripts/summarize_pdf.py" summarize "PDF文件名" --keywords "关键词"` |

### 实际操作流程

#### 流程 1: 完整提取（推荐用于后续 CSV 生成）

```bash
cd C:\Users\25156\Desktop\dbcjson5

# 第一步：提取 PDF
uv run python ".github/skills/pdf-summary/scripts/extract_pdf.py" "绿控传动TMCU通讯协议1C.pdf" \
  --output outputs/pdf_extracted.txt

# 第二步：查看提取结果
Get-Content outputs/pdf_extracted.txt -Encoding UTF8 | Select-Object -First 100

# 第三步：大模型读取 pdf_extracted.txt，识别报文和信号，生成 Unified CSV
```

#### 流程 2: 搜索特定信息

```bash
cd C:\Users\25156\Desktop\dbcjson5

# 搜索与电机相关的内容
uv run python ".github/skills/pdf-summary/scripts/summarize_pdf.py" summarize \
  "绿控传动TMCU通讯协议1C.pdf" \
  --keywords "报文,信号,ID,波特率,转速,扭矩" \
  --no-content \
  --output outputs/protocol_analysis.txt
```

---

## 第四步：输出处理

### 输出文件说明

| 文件 | 说明 | 生成方式 |
|------|------|---------|
| `pdf_extracted.txt` | extract_pdf.py 的完整输出 | `extract_pdf.py ... --output` |
| `protocol_analysis.txt` | summarize_pdf.py 的统计/关键词分析 | `summarize_pdf.py summarize ... --output` |

### 后续处理

```bash
# 验证文件生成
ls -la outputs/

# 统计提取字符数
Get-Content outputs/pdf_extracted.txt -Encoding UTF8 | Measure-Object -Character

# 大模型处理
# 1. 读取 pdf_extracted.txt 内容
# 2. 识别报文和信号定义
# 3. 生成 Unified CSV 格式
```

---

## 完整使用示例

### 场景 1: 从零开始处理 PDF 生成 CSV

```bash
# 步骤 1: 进入项目目录
cd C:\Users\25156\Desktop\dbcjson5

# 步骤 2: 同步依赖（首次运行）
uv sync

# 步骤 3: 提取 PDF 内容
uv run python ".github/skills/pdf-summary/scripts/extract_pdf.py" \
  "绿控传动TMCU通讯协议1C.pdf" \
  --output outputs/protocol_full_text.txt

# 步骤 4: 大模型读取 outputs/protocol_full_text.txt
# 识别以下信息：
# - 波特率：500kbps
# - 字节序：Intel (little_endian)
# - 报文定义表（PGN, ID, 长度, 周期）
# - 信号定义表（起始位, 长度, 范围, 单位, 偏移, 比例）

# 步骤 5: 大模型生成 Unified CSV
# 输出文件：outputs/protocol_unified.csv
```

### 场景 2: 搜索特定协议参数

```bash
cd C:\Users\25156\Desktop\dbcjson5

# 只搜索与电机控制相关的内容
uv run python ".github/skills/pdf-summary/scripts/summarize_pdf.py" summarize \
  "绿控传动TMCU通讯协议1C.pdf" \
  --keywords "电机,IPU,VCU,MCU,报文,信号,扭矩,转速" \
  --no-stats \
  --output outputs/motor_control_keywords.txt
```

### 场景 3: 只提取统计信息

```bash
cd C:\Users\25156\Desktop\dbcjson5

uv run python ".github/skills/pdf-summary/scripts/extract_pdf.py" \
  "绿控传动TMCU通讯协议1C.pdf" \
  --no-content
```

---

## 功能特性

### extract_pdf.py

✅ 直接使用 pdfplumber，无额外依赖  
✅ 完整提取所有页面的文本和表格  
✅ 显示提取统计信息（页数、字符数、表格数）  
✅ 灵活的输出选项（终端 / 文件）  
✅ 适合大模型处理的清晰输出格式  

### summarize_pdf.py

✅ 基于 Typer 框架的现代化 CLI  
✅ 灵活的命令行选项  
✅ 彩色终端输出  
✅ 内置关键词搜索  
✅ 统计分析功能  
✅ 完整的错误处理  

---

## 依赖

```toml
dependencies = [
    "pdfplumber>=0.10.0",  # PDF 文本提取
    "typer>=0.9.0",        # CLI 框架
    "rich>=13.0.0",        # 彩色输出（extract_pdf.py）
]
```

---

## 故障排除

### 问题 1: "找不到 PDF 文件"

```bash
# 检查 PDF 是否存在
dir C:\Users\25156\Desktop\dbcjson5\*.pdf

# 使用完整路径
uv run python ".github/skills/pdf-summary/scripts/extract_pdf.py" \
  "C:\Users\25156\Desktop\dbcjson5\protocol.pdf"
```

### 问题 2: "UnicodeEncodeError" 编码错误

```bash
# 设置 Python 编码为 UTF-8
$env:PYTHONIOENCODING='utf-8'

# 然后运行命令
uv run python ".github/skills/pdf-summary/scripts/extract_pdf.py" "协议.pdf"
```

### 问题 3: "No module named 'pdfplumber'"

```bash
# 同步依赖
cd C:\Users\25156\Desktop\dbcjson5
uv sync

# 验证安装
uv run python -c "import pdfplumber; print('OK')"
```

### 问题 4: uv 命令未找到

```bash
# 安装 uv
python -m pip install uv

# 验证
uv --version
```

---

## 参考资源

- [pdfplumber 文档](https://github.com/jsvine/pdfplumber)
- [Typer 文档](https://typer.tiangolo.com/)
- [uv 文档](https://docs.astral.sh/uv/)
