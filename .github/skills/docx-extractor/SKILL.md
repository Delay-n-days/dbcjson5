---
name: docx-extractor
description: >
  从Word文档(.docx)中提取文本和表格内容的工具。
  支持提取段落文本、表格数据，并保存为纯文本格式。
  适用场景：处理CAN通信协议Word文档、技术规范文档、报告文档等。
  当用户提到 "提取Word文档"、"docx文本提取"、"Word转文本"、
  "提取表格"、"协议文档提取"、"Word内容提取" 等关键词时，必须使用本 skill。
---

# Word文档提取工具 (DOCX Extractor)

## 任务概述

从任意Word文档(.docx)中提取全部文本内容和表格数据，保存为纯文本格式文件。
提取的内容按照文档原始顺序排列，保持段落和表格的结构关系。

**主要功能:**
- ✅ 提取所有段落文本
- ✅ 提取所有表格内容（保留行列结构）
- ✅ 按文档顺序输出（段落和表格交替）
- ✅ 支持中文和特殊字符
- ✅ 统计信息展示（段落数、表格数、字符数）
- ✅ 彩色控制台输出

**适用场景:**
- CAN通信协议文档内容提取
- 技术规范文档文本分析
- 报告文档数据提取
- 文档内容预处理

---

## 第一步：环境准备

### 1.1 检查Python环境

需要Python 3.8或更高版本：

```bash
python --version
# 或
python3 --version
```

### 1.2 验证uv工具

本工具使用uv管理依赖：

```bash
uv --version
```

如果未安装uv，请参考项目文档安装。

### 1.3 所需依赖

本Skill依赖以下Python包（已在`pyproject.toml`中定义）：

| 包名 | 版本 | 用途 |
|------|------|------|
| python-docx | >=1.1.0 | Word文档解析 |
| rich | >=13.0.0 | 彩色控制台输出 |

---

## 第二步：输入文件准备

### 2.1 支持的文件格式

| 格式 | 扩展名 | 是否支持 |
|------|--------|---------|
| Word 2007+ | `.docx` | ✅ 是 |
| Word 97-2003 | `.doc` | ❌ 否（需先转换为.docx） |
| Rich Text | `.rtf` | ❌ 否 |

### 2.2 文件位置

- 可以是本地文件的绝对路径
- 可以是相对路径
- 支持包含中文的路径

### 2.3 文件要求

- 文件必须存在且可读
- 文件扩展名必须为`.docx`
- 文件内容应为有效的Word文档格式

---

## 第三步：提取文档内容

### 3.1 基本用法

```bash
# 提取文档内容到默认输出文件（同名.txt）
uv run python .github/skills/docx-extractor/scripts/extract_docx.py document.docx

# 指定输出文件
uv run python .github/skills/docx-extractor/scripts/extract_docx.py document.docx -o output.txt

# 使用完整路径
uv run python .github/skills/docx-extractor/scripts/extract_docx.py "e:\path\to\document.docx" -o outputs\result.txt
```

### 3.2 命令参数

| 参数 | 简写 | 必需 | 说明 | 示例 |
|------|------|------|------|------|
| docx_file | - | ✅ | 输入的Word文档路径 | `document.docx` |
| --output | -o | ❌ | 输出文本文件路径（默认：同名.txt） | `-o result.txt` |

### 3.3 输出格式

提取的文本文件结构如下：

```
文档: document.docx
======================================================================

段落文本内容1

段落文本内容2

【表格 1】
----------------------------------------------------------------------
行 1: 列1 | 列2 | 列3
行 2: 数据1 | 数据2 | 数据3
----------------------------------------------------------------------

段落文本内容3

【表格 2】
----------------------------------------------------------------------
行 1: 标题A | 标题B
行 2: 值A | 值B
----------------------------------------------------------------------
```

---

## 第四步：验证输出结果

### 4.1 检查输出文件

```bash
# Windows
type output.txt

# 查看文件大小
dir output.txt
```

### 4.2 统计信息

运行脚本后会显示统计信息：

```
     提取统计      
┏━━━━━━━━━━┳━━━━━━┓
┃ 指标     ┃ 值   ┃
┡━━━━━━━━━━╇━━━━━━┩
│ 段落数   │ 50   │
│ 表格数   │ 7    │
│ 总字符数 │ 9742 │
└──────────┴──────┘
```

### 4.3 验证内容完整性

- 检查段落数是否正确
- 检查表格数是否完整
- 验证特殊字符是否正确显示
- 确认表格结构是否保持

---

## 完整使用示例

### 示例1：提取CAN通信协议文档

```bash
# 提取JJE通信协议文档
uv run python .github/skills/docx-extractor/scripts/extract_docx.py \
  "e:\WorkSpace\fq\A867\协议\JJE通信协议V2.4.2.docx" \
  -o outputs\JJE_protocol.txt
```

**预期输出:**
```
✓ 文档打开成功
     提取统计      
┏━━━━━━━━━━┳━━━━━━┓
┃ 指标     ┃ 值   ┃
┡━━━━━━━━━━╇━━━━━━┩
│ 段落数   │ 50   │
│ 表格数   │ 7    │
│ 总字符数 │ 9742 │
└──────────┴──────┘
✓ 提取完成！
✓ 结果已保存到: outputs\JJE_protocol.txt
```

### 示例2：提取技术规范文档

```bash
# 提取MCU控制器规范
uv run python .github/skills/docx-extractor/scripts/extract_docx.py \
  spec.docx \
  -o spec_extracted.txt
```

### 示例3：批量提取（使用循环）

```bash
# PowerShell批量提取
$files = Get-ChildItem *.docx
foreach ($file in $files) {
    uv run python .github/skills/docx-extractor/scripts/extract_docx.py $file.FullName
}
```

---

## 命令参数详解

### extract_docx.py

```
用法: extract_docx.py [-h] [-o OUTPUT] docx_file

提取Word文档(DOCX)中的文本和表格内容

位置参数:
  docx_file             要提取的DOCX文件路径

可选参数:
  -h, --help            显示帮助信息并退出
  -o OUTPUT, --output OUTPUT
                        输出文本文件路径（默认: 与输入文件同名的.txt文件）

示例:
  # 提取DOCX文档内容并保存
  python extract_docx.py document.docx -o output.txt
  
  # 使用uv运行
  uv run python extract_docx.py document.docx -o output.txt
```

---

## 功能特性

### 核心特性

- ✅ **段落提取**: 按文档顺序提取所有非空段落
- ✅ **表格提取**: 提取所有表格，保留行列结构
- ✅ **顺序保持**: 严格按照文档元素顺序输出
- ✅ **编码支持**: 完整支持UTF-8编码，正确处理中文
- ✅ **彩色输出**: 使用Rich库提供美观的控制台输出
- ✅ **统计信息**: 自动统计段落数、表格数、字符数

### 输出特性

- ✅ **格式化表格**: 使用分隔线和行号清晰展示表格
- ✅ **单元格处理**: 自动去除单元格内换行符
- ✅ **空格处理**: 去除多余空白字符
- ✅ **标题标记**: 使用【表格 N】标记每个表格

### 错误处理

- ✅ **文件验证**: 检查文件是否存在
- ✅ **格式验证**: 验证DOCX文件格式
- ✅ **异常捕获**: 捕获并显示有意义的错误信息
- ✅ **退出码**: 正确返回0(成功)或1(失败)

---

## 依赖

### Python包依赖

```toml
[project]
name = "docx-extractor"
version = "1.0.0"
description = "Extract text and tables from Word documents"
requires-python = ">=3.8"
dependencies = [
    "python-docx>=1.1.0",
    "rich>=13.0.0",
]
```

### 系统依赖

- Python 3.8+
- uv (包管理器)
- Windows / Linux / macOS

---

## 故障排除

### 问题1: 无法打开文档

**错误信息:**
```
❌ 无法打开文档: [Errno 2] No such file or directory
```

**解决方案:**
- 检查文件路径是否正确
- 确认文件确实存在
- 使用绝对路径而非相对路径
- 检查路径中的中文字符是否正确

### 问题2: 不是有效的DOCX文件

**错误信息:**
```
❌ 无法打开文档: File is not a zip file
```

**解决方案:**
- 确认文件是.docx格式（Word 2007+）
- 如果是.doc文件，请先用Word转换为.docx
- 检查文件是否损坏，尝试在Word中打开

### 问题3: 缺少依赖

**错误信息:**
```
ModuleNotFoundError: No module named 'docx'
```

**解决方案:**
```bash
# 使用uv同步依赖
uv sync

# 或手动安装
pip install python-docx rich
```

### 问题4: 编码错误

**错误信息:**
```
UnicodeEncodeError: 'charmap' codec can't encode characters
```

**解决方案:**
- 确保输出文件使用UTF-8编码
- 脚本已默认使用UTF-8，检查终端编码设置

### 问题5: 表格内容丢失

**症状:** 某些表格内容没有被提取

**解决方案:**
- 检查Word文档中是否存在嵌套表格（暂不支持）
- 验证表格是否为真正的Word表格而非文本框
- 尝试在Word中重新创建表格

---

## 最佳实践

### 1. 文件组织

```
project/
├── inputs/          # 输入的DOCX文件
│   ├── protocol1.docx
│   └── protocol2.docx
└── outputs/         # 提取的文本文件
    ├── protocol1.txt
    └── protocol2.txt
```

### 2. 命名规范

- 使用有意义的输出文件名
- 保持输入输出文件名关联
- 避免中文路径（虽然支持，但可能有兼容性问题）

### 3. 批量处理

创建批处理脚本：

```powershell
# batch_extract.ps1
$inputDir = "inputs"
$outputDir = "outputs"

Get-ChildItem "$inputDir\*.docx" | ForEach-Object {
    $outputFile = "$outputDir\$($_.BaseName).txt"
    uv run python .github/skills/docx-extractor/scripts/extract_docx.py $_.FullName -o $outputFile
}
```

### 4. 后续处理

提取的文本可用于：
- 协议分析（配合pdf-to-can-csv skill）
- 文档搜索和索引
- 内容对比
- 数据提取和结构化

---

## 相关 Skills

- **pdf-to-can-csv**: 将CAN协议文档转换为CSV格式
- **csv-to-dbc**: 将CSV格式转换为DBC文件
- **pdf-summary**: 提取PDF文档内容

---

## 参考资源

- [python-docx 官方文档](https://python-docx.readthedocs.io/)
- [Rich 库文档](https://rich.readthedocs.io/)
- [Word Open XML 规范](https://learn.microsoft.com/en-us/office/open-xml/word/)

---

## 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0.0 | 2026-03-11 | 初始版本，支持文本和表格提取 |
