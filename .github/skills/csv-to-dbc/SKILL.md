---
name: csv-to-dbc
description: >
  使用内置的 csv2dbc.py 脚本将统一 CSV 格式（Unified CSV）转换为 CAN DBC 文件。
  自动配置 uv 环境、安装 cantools 依赖并执行转换。
  适用场景：用户上传了 unified CSV 文件，需要生成 DBC 文件；
  或用户提到 "CSV转DBC"、"生成DBC"、"csv2dbc"、"导出DBC"、"CAN数据库文件"、
  "DBC文件生成"、"cantools生成"、"从CSV生成DBC"、"转换DBC" 等关键词时，必须使用本 skill。
  本 skill 内置 csv2dbc.py 脚本，无需用户额外上传转换工具。
---

# CSV → DBC 转换 Skill

## 任务概述

将符合 Unified CSV 格式的报文/信号定义表，通过内置的 `csv2dbc.py` 脚本转换为标准 CAN DBC 文件。
本 skill 内置转换脚本，完整流程：环境准备 → uv 安装 → 依赖配置 → 执行转换 → 验证输出 → 交付。

> ⚠️ **环境配置**：先参照 `uv-project-runner` skill 完成 uv 安装与 PATH 配置。

---

## 第一步：准备工作区

### 1.1 确认输入文件

| 文件 | 来源 | 说明 |
|------|------|------|
| `*_unified.csv` | `/mnt/user-data/uploads/` 或 `/mnt/user-data/outputs/` | 输入 CSV（必须） |
| `csv2dbc.py` | **本 skill 内置** `scripts/csv2dbc.py` | 转换脚本（无需用户上传） |
| `pyproject.toml` | **本 skill 内置** `scripts/pyproject.toml` | 依赖配置（无需用户上传） |

### 1.2 建立工作目录

```bash
mkdir -p /home/claude/workspace/outputs

# 复制内置脚本（从 skill 目录）
SKILL_DIR=$(find /mnt/skills -name "csv-to-dbc" -type d 2>/dev/null | head -1)
cp "$SKILL_DIR/scripts/csv2dbc.py" /home/claude/workspace/
cp "$SKILL_DIR/scripts/pyproject.toml" /home/claude/workspace/

# 查找并复制用户的 CSV 文件
CSV_FILE=$(find /mnt/user-data -name "*unified*.csv" 2>/dev/null | head -1)
if [ -z "$CSV_FILE" ]; then
    CSV_FILE=$(find /mnt/user-data -name "*.csv" 2>/dev/null | head -1)
fi
echo "使用 CSV: $CSV_FILE"
cp "$CSV_FILE" /home/claude/workspace/

ls -la /home/claude/workspace/
```

---

## 第二步：配置 uv 环境

参照 `uv-project-runner` skill 执行完整安装流程：

```bash
# 检测并安装 uv
which uv 2>/dev/null || {
    echo "安装 uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh 2>/dev/null || \
    pip install uv --break-system-packages
}

# 配置 PATH
export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"

# 同步依赖
cd /home/claude/workspace
uv sync

# 验证 cantools
uv run python -c "import cantools; print('✓ cantools', cantools.__version__)"
```

---

## 第三步：执行转换

### 3.1 查看帮助

```bash
cd /home/claude/workspace
export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"
uv run python csv2dbc.py --help
```

或使用 PowerShell（Windows）：

```powershell
cd C:\path\to\workspace
uv run python csv2dbc.py --help
```

输出说明：
```
Arguments:
  unified_csv   统一 CSV 文件路径  [required]

Options:
  -o, --output  输出 DBC 文件路径
  -e, --encoding  CSV 编码 [default: gb2312]
```

### 3.2 执行转换

```bash
cd /home/claude/workspace
export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"

# 自动检测 CSV 文件名
CSV=$(ls *.csv | head -1)
echo "转换: $CSV"

uv run python csv2dbc.py "$CSV" \
    --output "outputs/$(basename $CSV .csv).dbc" \
    --encoding utf-8
```

或 PowerShell（Windows）：

```powershell
cd C:\path\to\workspace

# 自动检测 CSV 文件名
$CSV = Get-ChildItem -Filter "*.csv" | Select-Object -First 1 -ExpandProperty Name
echo "转换: $CSV"

uv run python csv2dbc.py "$CSV" `
    --output "outputs\$($CSV -replace '\.csv$', '.dbc')" `
    --encoding utf-8
```

### 3.3 编码选择

```bash
# 检测文件编码
file *.csv
python3 -c "
import chardet
with open('data.csv', 'rb') as f:
    result = chardet.detect(f.read())
print(result)
"

# UTF-8 文件
uv run python csv2dbc.py "data.csv" --encoding utf-8

# GBK/GB2312 文件（默认）
uv run python csv2dbc.py "data.csv" --encoding gb2312
```

---

## 第四步：验证输出

### 4.1 检查转换日志

成功输出示例：
```
正在读取统一 CSV: data.csv
警告: 原始 DBC 文件不存在，从 CSV 数据构建数据库
正在生成 DBC 文件...
✓ 验证成功! 包含 16 条消息
✓ 输出文件: outputs/data.dbc
```

### 4.2 验证 DBC 内容

```bash
cd /home/claude/workspace
export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"

# 统计消息和信号数量
echo "消息数: $(grep -c '^BO_ ' outputs/*.dbc)"
echo "信号数: $(grep -c '^ SG_ ' outputs/*.dbc)"

# cantools 深度验证
uv run python -c "
import cantools
db = cantools.database.load_file('outputs/$(ls outputs/*.dbc | head -1 | xargs basename)')
print(f'✓ 消息数: {len(db.messages)}')
for msg in sorted(db.messages, key=lambda m: m.frame_id):
    print(f'  0x{msg.frame_id:08X}  {msg.name:<40} {len(msg.signals)} 个信号')
"
```

---

## 第五步：错误处理

### 5.1 常见错误

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| `消息数量不匹配` | CSV 中有重复 ID 且名称相同 | 检查 ID 复用的报文是否用不同名称区分 |
| `UnicodeDecodeError` | 编码不匹配 | 切换 `--encoding utf-8` 或 `gb2312` |
| `KeyError: '消息ID'` | CSV 表头不完整 | 检查第一行是否有 19 列完整表头 |
| `ValueError` 数值字段 | 数字列含非数字字符 | 检查缩放系数、偏移等列 |
| `cantools SignalRangeError` | 信号超出消息边界 | 检查起始位 + 长度 ≤ 消息长度×8 |

### 5.2 CSV 快速诊断

```bash
cd /home/claude/workspace
export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"

uv run python -c "
import csv

csv_file = '$(ls *.csv | head -1)'
print(f'检查: {csv_file}')

with open(csv_file, encoding='utf-8') as f:
    reader = csv.reader(f)
    rows = list(reader)

print(f'总行数: {len(rows)}')
print(f'表头列数: {len(rows[0])}')
if len(rows[0]) != 19:
    print('⚠ 表头列数不是 19！')
    print('表头:', rows[0])

# 检查列数一致性
for i, row in enumerate(rows[1:], 2):
    if len(row) != 19:
        print(f'⚠ 第 {i} 行列数={len(row)}: {row[:3]}...')

# 统计消息数
msg_ids = set()
for row in rows[1:]:
    if row:
        msg_ids.add(row[0])
print(f'唯一消息 ID 数: {len(msg_ids)}')
"
```

### 5.3 信号位重叠检查

```bash
uv run python -c "
import csv
from collections import defaultdict

csv_file = '$(ls *.csv | head -1)'
signals_by_msg = defaultdict(list)

with open(csv_file, encoding='utf-8') as f:
    for row in csv.DictReader(f):
        key = (row['消息ID'], row['消息名称'])
        signals_by_msg[key].append((
            row['信号名称'],
            int(row['起始位']),
            int(row['长度(bit)'])
        ))

for (msg_id, msg_name), sigs in signals_by_msg.items():
    bits = {}
    for name, start, length in sigs:
        for b in range(start, start + length):
            if b in bits:
                print(f'⚠ {msg_name}: {name}(起始{start}) 与 {bits[b]} bit {b} 冲突')
                break
            bits[b] = name
print('位检查完成')
"
```

---

## 第六步：交付

```bash
cp /home/claude/workspace/outputs/*.dbc /mnt/user-data/outputs/
echo "输出文件:"
ls -la /mnt/user-data/outputs/*.dbc
```

使用 `present_files` 工具提供下载链接，并附：
- 共生成多少条消息、多少个信号
- 是否有验证警告
