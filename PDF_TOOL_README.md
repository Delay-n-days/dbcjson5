## PDF 提取和总结工具 - Typer CLI 版本

这是使用 **Typer** 框架重写的 PDF 文档处理工具，提供了灵活的命令行接口。

### 安装和运行

使用 `uv` 运行脚本（自动管理依赖）：

```bash
uv run summarize_pdf.py --help
```

### 可用命令

#### 1. `summarize` - 总结和提取 PDF 文档

提取 PDF 文档内容并进行统计分析。

```bash
# 基本用法 - 显示完整内容和统计
uv run summarize_pdf.py summarize <pdf_path>

# 只显示统计信息，隐藏完整内容
uv run summarize_pdf.py summarize <pdf_path> --no-content

# 只显示内容，隐藏统计
uv run summarize_pdf.py summarize <pdf_path> --no-stats

# 将输出保存到文件
uv run summarize_pdf.py summarize <pdf_path> --output result.txt

# 搜索自定义关键词（逗号分隔）
uv run summarize_pdf.py summarize <pdf_path> --keywords "转矩,电流,温度"
```

**选项：**
- `PDF_PATH` (必需) - PDF 文件路径
- `--output, -o` - 保存输出到文件
- `--content/--no-content` - 显示/隐藏完整内容 (默认: 显示)
- `--stats/--no-stats` - 显示/隐藏统计信息 (默认: 显示)
- `--keywords, -k` - 添加自定义搜索关键词

#### 2. `extract-text` - 提取纯文本

从 PDF 提取纯文本并保存到文件。

```bash
# 基本用法
uv run summarize_pdf.py extract-text <pdf_path> --output output.txt

# 快捷形式
uv run summarize_pdf.py extract-text <pdf_path> -o output.txt
```

**选项：**
- `PDF_PATH` (必需) - PDF 文件路径
- `--output, -o` (必需) - 输出文件路径

### 使用示例

```bash
# 示例 1: 分析协议文档
cd c:\Users\25156\Desktop\dbcjson5
uv run summarize_pdf.py summarize "../1_1_GTAKE扩展帧通讯协议V1.0（主驱） (1).pdf" --no-content

# 示例 2: 提取文本到文件
uv run summarize_pdf.py extract-text "../protocol.pdf" -o outputs/protocol_text.txt

# 示例 3: 搜索特定关键词
uv run summarize_pdf.py summarize "../protocol.pdf" --keywords "报文,信号,扭矩" --no-content
```

### 功能特性

✅ 支持彩色输出 (Red/Green/Yellow/Cyan)  
✅ 灵活的命令行选项  
✅ 关键词搜索和统计  
✅ 纯文本提取  
✅ 错误处理和验证  
✅ 自动 uv 依赖管理  

### 依赖

- `pdfplumber>=0.10.0` - PDF 文本提取
- `typer>=0.9.0` - CLI 框架

这些依赖在 `pyproject.toml` 中定义，`uv run` 会自动安装。
