---
name: uv-project-runner
description: >
  在工作区根目录配置统一的 uv 环境。所有 skill 脚本共用一个 Python 虚拟环境，
  依赖统一添加到工作区 pyproject.toml。【重点】不要在 skill 文件夹内创建独立虚拟环境。
  适用场景：运行 PDF 提取、CSV 转换、DBC 生成等 Python 脚本，
  或用户提到 "uv run"、"安装依赖"、"虚拟环境" 等关键词时。
---

# uv 工作区环境管理 Skill

## 🎯 核心原则（最重要）

### 【统一的工作区环境架构】

```
C:\Users\25156\Desktop\dbcjson5/              ← 工作区根目录
├── pyproject.toml                             ← ★ 所有依赖在此
├── uv.lock                                    ← 依赖锁文件
├── .venv/                                     ← ★ 唯一的虚拟环境（所有脚本共享）
├── .github/skills/
│   ├── pdf-summary/
│   │   ├── SKILL.md
│   │   └── scripts/
│   │       ├── extract_pdf.py                 ← 在工作区 .venv 中运行
│   │       └── summarize_pdf.py               ← 在工作区 .venv 中运行
│   ├── csv-to-dbc/
│   │   └── scripts/
│   │       └── csv2dbc.py                     ← 在工作区 .venv 中运行
│   └── ... （其他 skill）
├── outputs/                                   ← 所有脚本的输出目录
└── 其他项目文件
```

### ❌ 错误做法（禁止）

```bash
# ❌ 【禁止】在 skill 文件夹内创建虚拟环境
cd .github/skills/pdf-summary/scripts
uv sync  
# 这会导致：
# 1. 创建多个 .venv，浪费磁盘空间
# 2. 依赖分散，难以维护
# 3. 脚本无法相互调用
```

### ✅ 正确做法（必须遵循）

```bash
# ✅ 【必须】在工作区根目录操作
cd C:\Users\25156\Desktop\dbcjson5

# 1. 安装 uv（一次性）
python -m pip install uv

# 2. 分析脚本依赖
# 识别脚本中的 import 语句

# 3. 添加到工作区依赖（注意是"添加"而非"覆盖"）
uv add pdfplumber typer rich cantools

# 4. 在工作区环境中运行脚本
uv run python ".github/skills/pdf-summary/scripts/extract_pdf.py" "protocol.pdf"

# 所有脚本都用 uv run 在同一 .venv 中运行
```

### 为什么要统一环境

| 对比维度 | ❌ 独立虚拟环境（错误） | ✅ 统一工作区环境（正确） |
|---------|----------------------|------------------------|
| **磁盘占用** | 每个 skill 一个 .venv，重复浪费（500MB × 10个 skill = 5GB） | 只有一个 .venv，节省 90% 空间 |
| **依赖管理** | pyproject.toml 分散在各 skill 中，难以跟踪 | 集中在工作区 pyproject.toml，一目了然 |
| **脚本互调** | 环境不兼容，脚本无法相互调用 | 所有脚本使用相同环境，可相互集成 |
| **维护成本** | 升级依赖需要改多个地方，容易遗漏 | 只改一个 pyproject.toml，自动应用 |
| **下载网络** | 重复下载相同包 | 只下载一次 |

---

## 快速开始（5 分钟）

### 一次性初始化

```bash
# 1. 进入工作区根目录
cd C:\Users\25156\Desktop\dbcjson5

# 2. 安装 uv（如果还没装）
python -m pip install uv -q
uv --version

# 3. 同步依赖（使用已有的 pyproject.toml）
uv sync

# 完成！所有脚本现在都可以运行
```

### 运行任意脚本

```bash
# 从工作区根目录运行所有脚本
uv run python ".github/skills/pdf-summary/scripts/extract_pdf.py" "protocol.pdf"
uv run python ".github/skills/csv-to-dbc/scripts/csv2dbc.py" "data.csv"
```

---

## 详细步骤

## 第一步：安装 uv（全局工具，一次性）

### 1.1 检测 uv

```bash
# Windows
where uv
uv --version

# Linux/macOS
which uv
uv --version
```

### 1.2 安装 uv

```bash
# 推荐：pip 安装（各系统通用）
python -m pip install uv

# 验证
uv --version
```

### 1.3 备用安装方法

```bash
# Linux/macOS：官方安装脚本
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows：官方安装脚本
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 安装后需要配置 PATH
export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"
```

---

## 第二步：分析脚本依赖

### 2.1 查看现有 pyproject.toml

```bash
cd C:\Users\25156\Desktop\dbcjson5
cat pyproject.toml
```

### 2.2 手动识别新脚本的依赖

```python
# 方法 1：查看脚本的 import 语句
# C:\Users\25156\Desktop\dbcjson5\.github\skills\pdf-summary\scripts\extract_pdf.py
# 第一行通常会有：
import pdfplumber  # 需要安装
import typer       # 需要安装
from rich.console import Console  # 需要 rich 包
```

### 2.3 自动扫描依赖（Python 脚本）

```python
import ast
from pathlib import Path

# Python 标准库（无需安装）
STDLIB = {
    'os', 'sys', 'json', 'csv', 'pathlib', 'typing', 'collections',
    'itertools', 'functools', 'datetime', 'math', 'io', 're',
    'subprocess', 'shutil', 'tempfile', 'hashlib', 'base64',
    'traceback', 'copy', 'time', 'abc', 'enum', 'dataclasses'
}

# 扫描脚本
script_path = Path(".github/skills/pdf-summary/scripts/extract_pdf.py")
third_party = set()

tree = ast.parse(script_path.read_text(encoding='utf-8'))
for node in ast.walk(tree):
    if isinstance(node, ast.Import):
        for alias in node.names:
            pkg = alias.name.split('.')[0]
            if pkg not in STDLIB:
                third_party.add(pkg)
    elif isinstance(node, ast.ImportFrom):
        if node.module:
            pkg = node.module.split('.')[0]
            if pkg not in STDLIB:
                third_party.add(pkg)

print("需要安装的包:", sorted(third_party))
# 输出示例: {'pdfplumber', 'typer', 'rich'}
```

---

## 第三步：添加依赖到工作区

### 【重点】使用 uv add 而不是 uv sync

```bash
# ✅ 正确：添加依赖到工作区 pyproject.toml
cd C:\Users\25156\Desktop\dbcjson5
uv add pdfplumber typer rich cantools

# 这会：
# 1. 解析包的版本和依赖关系
# 2. 添加到 pyproject.toml
# 3. 生成/更新 uv.lock
# 4. 在 .venv 中安装包
```

### 添加示例

```bash
# 添加单个包
uv add pdfplumber

# 添加多个包
uv add typer rich cantools "pydantic>=2.0"

# 查看已添加的包
uv pip list
```

### 验证依赖安装

```bash
# 验证包可导入
uv run python -c "import pdfplumber, typer, rich; print('All packages OK')"

# 查看包版本
uv run python -c "import pdfplumber; print(pdfplumber.__version__)"
```

---

## 第四步：在工作区环境中运行脚本

### 4.1 基本运行方式

```bash
# 进入工作区根目录
cd C:\Users\25156\Desktop\dbcjson5

# 运行 skill 脚本（使用相对路径）
uv run python ".github/skills/pdf-summary/scripts/extract_pdf.py" "绿控传动TMCU通讯协议1C.pdf"

# 运行其他脚本
uv run python ".github/skills/csv-to-dbc/scripts/csv2dbc.py" "data.csv" --output "outputs/result.dbc"
```

### 4.2 带选项的运行

```bash
# 重定向输出到文件
uv run python ".github/skills/pdf-summary/scripts/extract_pdf.py" "protocol.pdf" > outputs/log.txt 2>&1

# 后台运行
uv run python ".github/skills/csv-to-dbc/scripts/csv2dbc.py" "data.csv" &

# 设置环境变量
$env:PYTHONIOENCODING='utf-8'
uv run python ".github/skills/pdf-summary/scripts/extract_pdf.py" "协议.pdf"
```

### 4.3 查看脚本帮助

```bash
# 大多数 skill 脚本都支持 --help
uv run python ".github/skills/pdf-summary/scripts/extract_pdf.py" --help

# Typer CLI 脚本
uv run python ".github/skills/pdf-summary/scripts/summarize_pdf.py" --help
```

---

## 第五步：管理工作区依赖

### 5.1 查看当前依赖

```bash
# 显示 pyproject.toml 中的依赖
cat pyproject.toml

# 显示已安装的包和版本
uv pip list
```

### 5.2 添加新的依赖

```bash
# 需要新包时，继续使用 uv add
uv add numpy pandas openpyxl

# 【不要】使用 pip install（会绕过 uv 依赖管理）
# ❌ pip install numpy
# ✅ uv add numpy
```

### 5.3 移除不需要的依赖

```bash
# 从 pyproject.toml 移除包
uv remove numpy

# 手动编辑 pyproject.toml 后，重新同步
uv sync
```

### 5.4 更新依赖

```bash
# 更新所有包到最新版本
uv pip install --upgrade

# 更新特定包
uv add "cantools>=42.0"
```

---

## 常见任务

### 任务 1：新增一个 skill，需要安装其依赖

```bash
# 1. 分析 skill 的 scripts/*.py 文件中的 import
# 假设需要 requests 和 beautifulsoup4

# 2. 添加到工作区依赖
cd C:\Users\25156\Desktop\dbcjson5
uv add requests beautifulsoup4

# 3. 在工作区环境中运行脚本
uv run python ".github/skills/new-skill/scripts/main.py"
```

### 任务 2：从头配置一个新项目

```bash
# 1. 创建工作区根目录
mkdir my-workspace
cd my-workspace

# 2. 初始化 pyproject.toml
uv init --python 3.12

# 3. 添加需要的包
uv add pdfplumber cantools typer

# 4. 创建脚本
mkdir -p scripts
echo "import pdfplumber; print('OK')" > scripts/test.py

# 5. 运行脚本
uv run python scripts/test.py
```

### 任务 3：在不同的机器上复现工作区环境

```bash
# 在新机器上：
# 1. 克隆或复制项目到新机器
cp -r my-project /path/to/new/machine

# 2. 进入项目目录
cd /path/to/new/machine

# 3. 同步依赖（uv.lock 保证完全一致）
uv sync

# 完成！所有包都被安装到 .venv，脚本可以运行
```

---

## 故障排除

### 问题 1："uv: command not found"

```bash
# 原因：uv 未安装或 PATH 未配置
# 解决：

# 检查安装
python -m pip show uv

# 重新安装
python -m pip install --upgrade uv

# 验证
uv --version
```

### 问题 2："No module named 'xxx'"

```bash
# 原因：包未安装到 .venv
# 解决：

# 检查是否在 pyproject.toml 中
grep "xxx" pyproject.toml

# 如果没有，添加它
uv add xxx

# 重新同步
uv sync
```

### 问题 3："uv run 找不到脚本文件"

```bash
# 原因：路径错误或不在工作区根目录
# 解决：

# 确认在工作区根目录
pwd  # 应该是 C:\Users\25156\Desktop\dbcjson5

# 检查脚本文件是否存在
ls ".github/skills/pdf-summary/scripts/extract_pdf.py"

# 使用完整相对路径
uv run python ".github/skills/pdf-summary/scripts/extract_pdf.py"
```

### 问题 4："UnicodeEncodeError: 'gbk' codec can't encode"

```bash
# 原因：Windows 默认编码是 GBK，Python 输出中文时出错
# 解决：

# 设置 Python 编码为 UTF-8
$env:PYTHONIOENCODING='utf-8'

# 然后运行脚本
uv run python ".github/skills/pdf-summary/scripts/extract_pdf.py" "协议.pdf"
```

### 问题 5："在 skill 文件夹内创建了独立 .venv"

```bash
# 如果不小心在 skill 中运行了 uv sync：
# .github/skills/pdf-summary/.venv/  ← 这是错误的

# 删除它
rm -rf ".github/skills/pdf-summary/.venv"
rm -rf ".github/skills/pdf-summary/uv.lock"

# 回到工作区根目录重新同步
cd C:\Users\25156\Desktop\dbcjson5
uv sync
```

---

## 工作区初始化清单

- [ ] 安装 uv：`python -m pip install uv`
- [ ] 验证 uv：`uv --version`
- [ ] 进入工作区根目录：`cd C:\Users\25156\Desktop\dbcjson5`
- [ ] 查看 pyproject.toml：`cat pyproject.toml`
- [ ] 同步依赖：`uv sync`
- [ ] 验证依赖：`uv pip list`
- [ ] 尝试运行脚本：`uv run python ".github/skills/pdf-summary/scripts/extract_pdf.py" --help`
- [ ] 配置 PYTHONIOENCODING（Windows）：`$env:PYTHONIOENCODING='utf-8'`

---

## 快速参考

```bash
# === 初始化 ===
python -m pip install uv           # 安装 uv
cd C:\path\to\workspace             # 进入工作区
uv sync                             # 同步现有依赖

# === 依赖管理 ===
uv add package1 package2            # 添加包
uv remove package1                  # 移除包
uv pip list                         # 查看已安装
uv pip show package1                # 查看包详情

# === 运行脚本 ===
uv run python script.py             # 运行脚本
uv run python script.py --help      # 查看帮助
uv run python -c "import pkg; print(pkg.__version__)"  # 检查包版本

# === 诊断 ===
uv --version                        # 检查 uv 版本
which uv                            # 检查 uv 位置（Linux/macOS）
where uv                            # 检查 uv 位置（Windows）
cat pyproject.toml                  # 查看依赖列表
ls -la .venv                        # 检查虚拟环境位置
```

---

## 参考资源

- [uv 官方文档](https://docs.astral.sh/uv/)
- [uv 项目管理](https://docs.astral.sh/uv/guides/projects/)
- [pyproject.toml 规范](https://packaging.python.org/en/latest/specifications/pyproject-toml/)
