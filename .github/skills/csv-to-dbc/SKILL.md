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
#### 输入样例

严格按照 Unified CSV 格式输出，第一行是列名，后续每行一个信号：

```csv
消息ID,消息名称,消息长度,周期时间(ms),发送者,消息备注(JSON),信号名称,起始位,长度(bit),字节序,有符号,初值,缩放系数,偏移,最小值,最大值,单位,接收者,备注(JSON)
0x18FF5678,MCU2_STATUS5,8,,,,MCU1_VoltD,0,16,little_endian,否,,1,-30000,,,,,
0x18FF5678,MCU2_STATUS5,8,,,,MCU1_VoltQ,16,16,little_endian,否,,1,-30000,,,,,
0x1CFDD2F0,MCU2_STATUS4,8,,MCU2,,MCU2_Soft_ProtocolVer,8,4,little_endian,否,,0.1,2,,,,HCU,"{""0"": ""INIT"", ""1"": ""LV_PWR_UP"", ""2"": ""HV_PWR_UP"", ""3"": ""Idle"", ""4"": ""Speed Control"", ""5"": ""Torque Control"", ""6"": ""SHUTDWN(active capacitor discharge)"", ""7"": 
0x1CFDD2F0,MCU2_STATUS4,8,,MCU2,,MCU2_Rotation_Unit,34,2,little_endian,否,,1,0,0,3,,HCU,
0x1CFDD2F0,MCU2_STATUS4,8,,MCU2,,MCU2_soft_ver,40,24,little_endian,否,,1,0,0,16777215,,HCU,"{""0"": ""INIT"", ""1"": ""LV_PWR_UP"", ""2"": ""HV_PWR_UP"", ""3"": ""Idle"", ""4"": ""Speed Control"", ""5"": ""Torque Control"", ""6"": ""SHUTDWN(active capacitor discharge)"", ""7"": ""LV_PWR_DWN"", ""8"": ""FAULT""}"
0x18FF42F0,MCU2_STATUS1,8,,MCU2,,MCU2_Speed,0,16,little_endian,否,,1,-6000,-6000,59535,rpm,HCU,"{""description"": ""电机转速正负表示电机转向，转速为正时与发动机正常转动方向一致""}"
0x18FF42F0,MCU2_STATUS1,8,,MCU2,,MCU2_Torque,16,16,little_endian,否,,1,-3200,-3200,62335,Nm,HCU,"{""description"": ""转矩矩大于0为转矩方向与发动机转向相同""}"
0x18FF42F0,MCU2_STATUS1,8,,MCU2,,MCU2_DC_Current,32,16,little_endian,否,,1,-1000,-1000,64535,A,HCU,
0x18FF42F0,MCU2_STATUS1,8,,MCU2,,MCU2_IvtPwmTzFrc,48,8,little_endian,否,,1,0,,,,,
0x18FF42F0,MCU2_STATUS1,8,,MCU2,,MCU2_Fail_Grade,56,4,little_endian,否,,1,0,0,15,,HCU,"{""0"": ""No Fault"", ""1"": ""Warning(degraded)"", ""2"": ""Fault(zero torque output)"", ""3"": ""Fault(shut down MCU)"", ""4"": ""Serious Fault(need to stop the vehicle)""}"
0x18FF42F0,MCU2_STATUS1,8,,MCU2,,MCU2_Work_Mode,60,4,little_endian,否,,1,0,0,15,,HCU,"{""0"": ""Ready（上电完成 MCU 已开管不 控制）"", ""1"": ""Enable（上电完成，MCU 未开管）"", ""2"": ""PowerUp（低压上电，准备上高压 或者高压上电过程中）"", ""3"": ""Error(错误)"", ""4"": ""防溜坡控制状态"", ""5"": ""转速模式扭矩受限"", ""6"": ""扭矩模式转速受限"", ""7"": ""快速下电中"", ""8"": ""扭矩控制"", ""9"": ""速度控制""}"
```

## 第一步：准备工作区

### 1.1 确认输入文件

| 文件 | 来源 | 说明 |
|------|------|------|
| `*_unified.csv` | `/mnt/user-data/uploads/` 或 `/mnt/user-data/outputs/` | 输入 CSV（必须） |
| `csv2dbc.py` | **本 skill 内置** `scripts/csv2dbc.py` | 转换脚本（无需用户上传） |
| `pyproject.toml` | **本 skill 内置** `scripts/pyproject.toml` | 依赖配置（无需用户上传） |


## 第二步：查看帮助

```bash

(dbcjson5) PS C:\Users\25156\Desktop\dbcjson5> uv run python ".github/skills/csv-to-dbc/scripts/csv2dbc.py" --help

 Usage: csv2dbc.py [OPTIONS] COMMAND [ARGS]...

 CSV 到 DBC 文件转换工具

╭─ Options ──────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the       │
│                               current shell.                   │
│ --show-completion             Show completion for the current  │
│                               shell, to copy it or customize   │
│                               the installation.                │
│ --help                        Show this message and exit.      │
╰────────────────────────────────────────────────────────────────╯
╭─ Commands ─────────────────────────────────────────────────────╮
│ convert  从统一的 CSV 表生成 DBC 文件                          │
│ version  显示版本信息                                          │
╰────────────────────────────────────────────────────────────────╯

```

## 第三步: 运行

```bash
uv run python ".github/skills/csv-to-dbc/scripts/csv2dbc.py" convert outputs/{csvname}.csv -o outputs/{dbcname}.dbc -e utf-8
```

## 第三步：错误处理

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
交付完成即可 无需生成报告

```bash
cp /home/claude/workspace/outputs/*.dbc /mnt/user-data/outputs/
echo "输出文件:"
ls -la /mnt/user-data/outputs/*.dbc
```

使用 `present_files` 工具提供下载链接，并附：
- 共生成多少条消息、多少个信号
- 是否有验证警告
