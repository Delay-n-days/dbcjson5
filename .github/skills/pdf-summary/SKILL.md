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

### 使用示例

#### 1. 提取并保存到文件

```bash
# 指定具体的 PDF 文件
uv run python ".github/skills/pdf-summary/scripts/extract_pdf.py" "xxx.pdf" --output outputs/xxx.txt
# 失败后使用
# 指定具体的 PDF 文件
uv run python ".github/skills/pdf-summary/scripts/summarize_pdf.py" "xxx.pdf" --output outputs/xxx.txt
```
