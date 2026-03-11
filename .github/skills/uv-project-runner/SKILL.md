---
name: uv-project-runner
description: >
  使用 uv 工具管理 Python 项目依赖并运行脚本。自动检测 uv 是否存在、自动安装、
  自动扫描脚本依赖并初始化项目环境。适用场景：用户上传了 Python 脚本需要运行；
  或用户提到 "uv run"、"uv 工程"、"pyproject.toml"、"安装依赖"、"运行python脚本"、
  "虚拟环境"、"cantools"、"python 依赖管理"、"执行脚本" 等关键词时，必须使用本 skill。
  特别适用于运行 csv2dbc.py、cantools 等工具脚本。
---

# uv Python 项目自动配置与运行 Skill

## 任务概述

全自动完成：检测 uv → 安装 uv → 扫描依赖 → 初始化项目 → 安装依赖 → 运行脚本。
无论用户是否提供 `pyproject.toml`，本 skill 都能完成环境配置。

---

## 第一步：检测并安装 uv

### 1.1 检测 uv 是否可用

```bash
which uv 2>/dev/null && uv --version
```

### 1.2 若未找到 uv，自动检测操作系统并安装

```bash
python3 - << 'PYEOF'
import subprocess, sys, os, platform

def run(cmd, shell=True):
    r = subprocess.run(cmd, shell=shell, capture_output=True, text=True)
    print(r.stdout); print(r.stderr)
    return r.returncode

# 检测系统
system = platform.system()  # 'Linux', 'Darwin', 'Windows'
print(f"操作系统: {system} {platform.machine()}")

# 检测 uv
result = subprocess.run(['which', 'uv'], capture_output=True, text=True)
if result.returncode == 0:
    print(f"uv 已存在: {result.stdout.strip()}")
    sys.exit(0)

# 按系统安装
if system in ('Linux', 'Darwin'):
    print("使用 curl 安装 uv...")
    rc = run("curl -LsSf https://astral.sh/uv/install.sh | sh")
    if rc != 0:
        # 备用：pip 安装
        print("curl 安装失败，尝试 pip 安装...")
        run(f"{sys.executable} -m pip install uv --break-system-packages")
elif system == 'Windows':
    print("使用 PowerShell 安装 uv...")
    rc = run('powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"')
    if rc != 0:
        run(f"{sys.executable} -m pip install uv --break-system-packages")
else:
    print(f"未知系统 {system}，使用 pip 安装...")
    run(f"{sys.executable} -m pip install uv --break-system-packages")
PYEOF
```

### 1.3 配置 uv 到 PATH（curl 安装后需要）

```bash
# curl 安装的 uv 默认在 ~/.cargo/bin 或 ~/.local/bin
export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"

# 验证
uv --version || python3 -m uv --version
```

> **提示**：后续所有 uv 命令都在配置了 PATH 的 shell 中执行，或使用 `python3 -m uv` 替代

---

## 第二步：准备工作目录

```bash
mkdir -p /home/claude/workspace/outputs

# 复制上传的脚本和配置
cp /mnt/user-data/uploads/*.py /home/claude/workspace/ 2>/dev/null || true
cp /mnt/user-data/uploads/pyproject.toml /home/claude/workspace/ 2>/dev/null || true

# 复制输入数据文件
cp /mnt/user-data/uploads/*.csv /home/claude/workspace/ 2>/dev/null || true
cp /mnt/user-data/outputs/*.csv /home/claude/workspace/ 2>/dev/null || true

echo "工作目录内容:"
ls -la /home/claude/workspace/
```

---

## 第三步：自动扫描脚本依赖

### 3.1 若有 pyproject.toml，直接读取依赖

```bash
cat /home/claude/workspace/pyproject.toml
```

### 3.2 若无 pyproject.toml，自动扫描 Python 文件中的 import

```python
import ast, os, sys
from pathlib import Path

# Python 标准库模块列表（不需要安装）
STDLIB = set(sys.stdlib_module_names) if hasattr(sys, 'stdlib_module_names') else {
    'os', 'sys', 'json', 'csv', 'pathlib', 'typing', 'collections',
    'itertools', 'functools', 'datetime', 'math', 'io', 're',
    'subprocess', 'shutil', 'tempfile', 'hashlib', 'base64',
    'traceback', 'copy', 'time', 'abc', 'enum', 'dataclasses'
}

workspace = Path('/home/claude/workspace')
third_party = set()

for py_file in workspace.glob('*.py'):
    try:
        tree = ast.parse(py_file.read_text(encoding='utf-8'))
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
    except Exception as e:
        print(f"解析 {py_file.name} 失败: {e}")

print("检测到第三方依赖:", sorted(third_party))
```

### 3.3 自动生成 pyproject.toml（若不存在）

```python
from pathlib import Path

# 依赖包名映射（import name → PyPI package name）
IMPORT_TO_PACKAGE = {
    'cantools': 'cantools>=41.0.0',
    'typer': 'typer>=0.9.0',
    'pandas': 'pandas>=2.0.0',
    'openpyxl': 'openpyxl>=3.1.0',
    'docx': 'python-docx>=1.0.0',
    'yaml': 'pyyaml>=6.0',
    'requests': 'requests>=2.28.0',
    'numpy': 'numpy>=1.24.0',
    'click': 'click>=8.0.0',
    'rich': 'rich>=13.0.0',
    'pydantic': 'pydantic>=2.0.0',
}

# third_party 来自上一步的扫描结果
deps = [IMPORT_TO_PACKAGE.get(pkg, pkg) for pkg in sorted(third_party)]

toml_content = f'''[project]
name = "workspace-project"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
{chr(10).join(f'    "{dep}",' for dep in deps)}
]
'''

Path('/home/claude/workspace/pyproject.toml').write_text(toml_content)
print("已生成 pyproject.toml:")
print(toml_content)
```

---

## 第四步：安装依赖

```bash
cd /home/claude/workspace
export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"

# 优先用 uv sync（读取 pyproject.toml）
uv sync 2>&1 && echo "✓ uv sync 成功" || {
    echo "uv sync 失败，尝试 uv pip install..."
    uv pip install $(python3 -c "
import tomllib
with open('pyproject.toml','rb') as f:
    data = tomllib.load(f)
deps = data.get('project', {}).get('dependencies', [])
print(' '.join(f'\"{d}\"' for d in deps))
    ")
}
```

### 4.1 验证依赖安装

```bash
cd /home/claude/workspace
export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"

# 验证关键包可导入
uv run python -c "
import importlib, sys
packages = ['cantools', 'typer']  # 根据实际扫描结果调整
for pkg in packages:
    try:
        m = importlib.import_module(pkg)
        version = getattr(m, '__version__', 'unknown')
        print(f'✓ {pkg} {version}')
    except ImportError as e:
        print(f'✗ {pkg}: {e}')
"
```

---

## 第五步：运行脚本

### 5.1 标准运行方式

```bash
cd /home/claude/workspace
export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"

uv run python script.py [参数] 2>&1
```

### 5.2 常见参数模式

```bash
# 位置参数
uv run python csv2dbc.py "input.csv"

# 带选项
uv run python csv2dbc.py "input.csv" --output "outputs/result.dbc" --encoding utf-8

# 查看帮助
uv run python csv2dbc.py --help
```

### 5.3 uv 不可用时的降级方案

```bash
# 使用 python -m uv
python3 -m uv run python script.py [参数]

# 或直接用系统 Python + pip 安装
pip install cantools typer --break-system-packages
python3 script.py [参数]
```

---

## 第六步：错误处理

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| `uv: command not found` | uv 未安装或 PATH 未配置 | 重新执行第一步，检查 `export PATH` |
| `No module named 'xxx'` | 依赖未安装 | `uv pip install xxx` |
| `No pyproject.toml` | 未在项目目录 | `cd /home/claude/workspace` |
| `UnicodeDecodeError` | 文件编码问题 | 添加 `--encoding utf-8` 或 `gb2312` |
| `SSL: CERTIFICATE_VERIFY_FAILED` | 网络证书问题 | `pip install uv --break-system-packages` 备用 |

---

## 快速参考

```bash
# 检测 uv
which uv && uv --version

# Linux/macOS 安装
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows 安装
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 备用安装（任意系统）
pip install uv --break-system-packages

# 配置 PATH
export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"

# 同步依赖
cd /project && uv sync

# 运行脚本
uv run python script.py [参数]

# 查看已安装包
uv pip list
```
