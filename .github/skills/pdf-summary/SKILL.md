---
name: pdf-summary
description: >
  提取并总结 CAN 通讯协议 PDF 文档。
  支持完整的文本提取、统计分析、关键词搜索。
  使用 Typer 框架实现的现代化 CLI 工具。
  备选方案：若 summarize_pdf.py 无法读取 PDF，使用 extract_pdf.py 提取完整的 PDF 文本和表格。
  适用场景：用户需要提取 PDF 中的协议信息、报文定义、信号参数等内容，或从 PDF 中提取内容用于大模型处理生成 CSV。
  当用户提到 "提取PDF"、"总结协议"、"PDF转文本"、"协议文档摘要"、
  "CAN协议提取"、"电机控制器协议"、"通讯协议分析"、"PDF文本提取"、"PDF转CSV" 等关键词时，必须使用本 skill。
---

# PDF 提取和总结 Skill

## 任务概述

使用内置的 `summarize_pdf.py` 工具（基于 Typer 框架）提取并分析 PDF 文档，
提供完整的文本提取、统计分析、关键词搜索等功能。

若 `summarize_pdf.py` 无法读取 PDF，使用备选工具 `extract_pdf.py` 直接提取 PDF 内容供大模型处理。

---

## 第一步：环境准备

### 1.1 确认输入文件

| 文件 | 来源 | 说明 |
|------|------|------|
| `*.pdf` | `/mnt/user-data/uploads/` | 输入 PDF 文件（必须） |
| `summarize_pdf.py` | **本 skill 内置** `scripts/summarize_pdf.py` | CLI 脚本（无需用户上传） |
| `pyproject.toml` | **本 skill 内置** `scripts/pyproject.toml` | 依赖配置（无需用户上传） |

### 1.2 参照 uv-project-runner skill 完成 uv 安装

```bash
# 检测 uv
which uv && uv --version

# 若未安装，执行自动安装脚本
python3 - << 'PYEOF'
import subprocess, sys, platform
system = platform.system()
if subprocess.run(['which', 'uv'], capture_output=True).returncode != 0:
    if system in ('Linux', 'Darwin'):
        subprocess.run("curl -LsSf https://astral.sh/uv/install.sh | sh", shell=True)
    elif system == 'Windows':
        subprocess.run('powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"', shell=True)
    else:
        subprocess.run(f"{sys.executable} -m pip install uv --break-system-packages", shell=True)
PYEOF

export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"
```

---

## 第二步：建立工作目录

```bash
mkdir -p /home/claude/workspace/outputs

# 复制内置脚本和配置（从 skill 目录）
SKILL_DIR=$(find /mnt/skills -name "pdf-summary" -type d 2>/dev/null | head -1)
cp "$SKILL_DIR/scripts/summarize_pdf.py" /home/claude/workspace/
cp "$SKILL_DIR/scripts/pyproject.toml" /home/claude/workspace/

# 复制用户上传的 PDF 文件
PDF_FILE=$(find /mnt/user-data/uploads -name "*.pdf" 2>/dev/null | head -1)
if [ -n "$PDF_FILE" ]; then
    cp "$PDF_FILE" /home/claude/workspace/
    PDF_FILENAME=$(basename "$PDF_FILE")
    echo "已复制 PDF: $PDF_FILENAME"
fi

echo "工作目录内容："
ls -la /home/claude/workspace/
```

---

## 第三步：运行 PDF 总结工具

### 3.1 查看帮助信息

```bash
cd /home/claude/workspace
uv run summarize_pdf.py --help
```

### 3.2 使用 summarize 命令

提取和总结 PDF 文档内容：

```bash
# 基本用法 - 显示完整内容和统计
uv run summarize_pdf.py summarize "your_file.pdf"

# 只显示统计信息，隐藏完整内容
uv run summarize_pdf.py summarize "your_file.pdf" --no-content

# 只显示内容，隐藏统计
uv run summarize_pdf.py summarize "your_file.pdf" --no-stats

# 将输出保存到文件
uv run summarize_pdf.py summarize "your_file.pdf" --output result.txt

# 搜索自定义关键词（逗号分隔）
uv run summarize_pdf.py summarize "your_file.pdf" --keywords "报文,信号,转矩"

# 结合多个选项
uv run summarize_pdf.py summarize "your_file.pdf" \
  --no-content \
  --output /home/claude/workspace/outputs/stats.txt \
  --keywords "电流,温度,压力"
```

### 3.3 使用 extract-text 命令

从 PDF 提取纯文本并保存到文件：

```bash
uv run summarize_pdf.py extract-text "your_file.pdf" \
  --output /home/claude/workspace/outputs/extracted_text.txt
```

---

## 第四步：输出处理

### 4.1 输出文件说明

| 文件 | 说明 | 生成方式 |
|------|------|---------|
| `result.txt` | summarize 命令输出 | `--output` 选项 |
| `extracted_text.txt` | extract-text 命令输出 | 必需的 `--output` 选项 |

### 4.2 复制结果到输出目录

```bash
# 确保输出目录存在
mkdir -p /mnt/user-data/outputs

# 复制结果
cp /home/claude/workspace/outputs/*.txt /mnt/user-data/outputs/

echo "处理完成！结果已保存到 /mnt/user-data/outputs/"
```

---

## 完整使用示例

### 场景 1: 提取协议文档内容

```bash
cd /home/claude/workspace

# 列出上传的 PDF
ls -la *.pdf

# 提取并分析
uv run summarize_pdf.py summarize "GTAKE_Protocol.pdf" \
  --output outputs/protocol_summary.txt

# 查看结果
head -100 outputs/protocol_summary.txt
```

### 场景 2: 搜索特定参数

```bash
cd /home/claude/workspace

# 搜索与电机转速和转矩相关的内容
uv run summarize_pdf.py summarize "GTAKE_Protocol.pdf" \
  --no-content \
  --keywords "转速,转矩,扭矩,电流,温度" \
  --output outputs/keywords_analysis.txt
```

### 场景 3: 只提取纯文本

```bash
cd /home/claude/workspace

# 提取纯文本用于后续处理
uv run summarize_pdf.py extract-text "Protocol.pdf" \
  --output outputs/plain_text.txt

# 可以用其他工具进一步处理纯文本
grep "报文" outputs/plain_text.txt > outputs/messages.txt
```

---

## 命令参数详解

### summarize 命令

```
用法: summarize_pdf.py summarize [OPTIONS] PDF_PATH

参数:
  PDF_PATH              PDF 文件路径 [必需]

选项:
  --output, -o TEXT     将输出保存到文件 [可选]
  --content             显示完整文档内容 [默认: 显示]
  --no-content          隐藏完整文档内容
  --stats               显示统计信息 [默认: 显示]
  --no-stats            隐藏统计信息
  --keywords, -k TEXT   搜索自定义关键词，用逗号分隔 [可选]
  --help                显示帮助信息
```

### extract-text 命令

```
用法: summarize_pdf.py extract-text [OPTIONS] PDF_PATH

参数:
  PDF_PATH              PDF 文件路径 [必需]

选项:
  --output, -o TEXT     输出文件路径 [必需]
  --help                显示帮助信息
```

---

## 功能特性

✅ 支持多个 CLI 命令  
✅ 灵活的命令行选项  
✅ 彩色输出（Blue/Green/Yellow/Red）  
✅ 关键词搜索和统计  
✅ 纯文本提取  
✅ 文件输出选项  
✅ 完整的错误处理  
✅ 自动 uv 依赖管理  

---

## 依赖

- `pdfplumber>=0.10.0` - PDF 文本提取
- `typer>=0.9.0` - CLI 框架

依赖在 `pyproject.toml` 中定义，`uv run` 会自动安装。

---

## 故障排除

### 问题 1: "找不到 PDF 文件"

```bash
# 检查 PDF 是否存在
ls -la /home/claude/workspace/*.pdf

# 使用完整路径
uv run summarize_pdf.py summarize "/home/claude/workspace/protocol.pdf"
```

### 问题 2: summarize_pdf.py 无法读取 PDF（备选方案）

若 `summarize_pdf.py` 无法正确读取 PDF，可使用 `extract_pdf.py` 作为备选：

#### 使用 extract_pdf.py 代替

```bash
cd /home/claude/workspace

# 将以下脚本保存为 extract_pdf.py
cat > extract_pdf.py << 'EOF'
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pdfplumber

pdf_path = 'protocol.pdf'

try:
    with pdfplumber.open(pdf_path) as pdf:
        print(f'PDF 页数: {len(pdf.pages)}')
        
        # 提取所有页的文本和表格信息
        for i in range(len(pdf.pages)):
            page = pdf.pages[i]
            text = page.extract_text()
            tables = page.extract_tables()
            
            print(f'\n{"="*60}')
            print(f'第 {i+1} 页')
            print(f'{"="*60}')
            
            if text:
                print('文本内容（前1500字）:')
                print(text[:1500])
            
            if tables:
                print(f'\n找到 {len(tables)} 个表格')
                for j, table in enumerate(tables):
                    print(f'\n表格 {j+1}:')
                    for row in table[:10]:  # 显示前10行
                        print(row)
            
except Exception as e:
    print(f'错误: {e}')
EOF

# 运行 extract_pdf.py
uv run python extract_pdf.py > outputs/pdf_extracted.txt 2>&1

# 查看提取的内容
less outputs/pdf_extracted.txt
```

#### extract_pdf.py 优势

- ✅ 直接使用 pdfplumber，不依赖 Typer CLI 框架
- ✅ 完整提取 PDF 文本和表格，包含所有页
- ✅ 输出结构清晰，便于大模型处理
- ✅ 当 summarize_pdf.py 失败时的可靠备选方案
- ✅ 适合用于后续大模型识别和 CSV 生成

#### 处理流程

1. 运行 `extract_pdf.py` 生成 `pdf_extracted.txt`
2. 大模型读取完整的提取结果
3. 大模型识别波特率、字节序、报文定义、信号参数
4. 大模型直接输出 Unified CSV 格式（**不生成脚本**）

### 问题 3: "No module named 'pdfplumber'"

```bash
# 确保在正确的目录中运行
cd /home/claude/workspace

# 再次运行，uv 会自动安装依赖
uv run summarize_pdf.py summarize "your_file.pdf"
# 或
uv run python extract_pdf.py
```

### 问题 4: uv 命令未找到

```bash
# 配置 PATH
export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"

# 或使用完整路径
python3 -m uv run summarize_pdf.py summarize "your_file.pdf"
```

---

## 参考资源

- [pdfplumber 文档](https://github.com/jsvine/pdfplumber)
- [Typer 文档](https://typer.tiangolo.com/)
- [uv 文档](https://docs.astral.sh/uv/)
