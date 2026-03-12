---
name: dbc-to-comment
description: >
  从 DBC 文件提取信号信息，生成 C 语言注释格式的 JSON 文件。
  支持自动解析 DBC 中的所有信号，包括起始位、长度、系数、偏移、单位等信息，
  并转换为适合 C 代码注释的格式。
  适用场景：用户需要为 C 代码生成 CAN 信号注释文档；
  或用户提到 "DBC转注释"、"生成C注释"、"信号注释"、"DBC文档生成"、
  "C语言注释"、"信号信息提取"、"代码注释文档" 等关键词时，必须使用本 skill。
  本 skill 内置 dbc2comment.py 脚本，无需用户额外上传转换工具。
---

# DBC → C 注释 JSON 转换 Skill

## 任务概述

从标准 CAN DBC 文件中提取所有信号的详细信息（起始位、长度、系数、偏移、单位、描述等），
生成 C 语言风格的注释，并输出为 JSON 格式文件，便于在 C 代码中使用。

本 skill 内置 `dbc2comment.py` 脚本，使用 cantools 库解析 DBC 文件。

---

## 输出格式示例

生成的 JSON 文件格式如下：

```json
[
    {
        "HVAS_AirPmpRadrT": "// HVAS_AirPmpRadrT\t起始位:16\t长度:8\t系数:1\t偏移量:0\t单位:°C\t气泵散热温度"
    },
    {
        "Motor_Speed": "// Motor_Speed\t起始位:0\t长度:16\t系数:1\t偏移量:-15000\t单位:rpm\t电机转速正负表示电机转向"
    },
    {
        "Fail_Grade": "// Fail_Grade\t起始位:48\t长度:4\t系数:1\t偏移量:0\t0:No Fault 1:Warning(degraded) 2:Fault(zero torque output) 3:Fault(shut down MCU)"
    }
]
```

每个信号包含：
- 信号名称作为键
- Tab 分隔的注释字符串，包括：
  - C 注释开头 `//`
  - 信号名称
  - 起始位（bit）
  - 长度（bit）
  - 系数（scale）
  - 偏移量（offset）
  - 单位（如果有）
  - 描述信息或枚举值（如果有）

---

## 使用方法

### 第一步：查看帮助

```bash
uv run python ".github/skills/dbc-to-comment/scripts/dbc2comment.py" --help
```

输出：
```
Usage: dbc2comment.py [OPTIONS] COMMAND [ARGS]...

  DBC 到 C 注释 JSON 转换工具

Options:
  --help  Show this message and exit.

Commands:
  convert  从 DBC 文件生成 C 语言注释 JSON 文件
  version  显示版本信息
```

### 第二步：转换 DBC 文件

#### 基本用法（默认 UTF-8 编码）

```bash
uv run python ".github/skills/dbc-to-comment/scripts/dbc2comment.py" convert <dbc文件路径>
```

**示例：**
```bash
uv run python ".github/skills/dbc-to-comment/scripts/dbc2comment.py" convert outputs/GTAKE_motor_250K.dbc
```

输出文件：`outputs/GTAKE_motor_250K_comment.json`（自动命名）

#### 指定输出文件

```bash
uv run python ".github/skills/dbc-to-comment/scripts/dbc2comment.py" convert <dbc文件路径> -o <输出文件路径>
```

**示例：**
```bash
uv run python ".github/skills/dbc-to-comment/scripts/dbc2comment.py" convert outputs/GTAKE_motor_250K.dbc -o outputs/motor_comments.json
```

#### 指定 DBC 文件编码（中文 DBC）

如果 DBC 文件包含中文且出现乱码，使用 `-e gb2312` 或 `-e gbk`：

```bash
uv run python ".github/skills/dbc-to-comment/scripts/dbc2comment.py" convert <dbc文件路径> -e gb2312
```

**示例：**
```bash
uv run python ".github/skills/dbc-to-comment/scripts/dbc2comment.py" convert outputs/GTAKE_motor_250K.dbc -o outputs/comments.json -e gb2312
```

#### 自定义 JSON 缩进

```bash
uv run python ".github/skills/dbc-to-comment/scripts/dbc2comment.py" convert <dbc文件路径> -i 2
```

**示例：**
```bash
uv run python ".github/skills/dbc-to-comment/scripts/dbc2comment.py" convert outputs/GTAKE_motor_250K.dbc -i 2
```

#### 不显示预览

```bash
uv run python ".github/skills/dbc-to-comment/scripts/dbc2comment.py" convert <dbc文件路径> --no-preview
```

---

## 命令参数说明

### convert 命令

| 参数 | 简写 | 类型 | 默认值 | 说明 |
|------|------|------|--------|------|
| `dbc_file` | - | 必填 | - | 输入的 DBC 文件路径 |
| `--output` | `-o` | 可选 | 自动生成 | 输出的 JSON 文件路径 |
| `--encoding` | `-e` | 可选 | `utf-8` | DBC 文件编码（utf-8/gb2312/gbk） |
| `--indent` | `-i` | 可选 | `4` | JSON 缩进空格数 |
| `--preview` | `-p` | 可选 | `True` | 显示前 10 条信号预览 |

---

## 典型工作流

### 场景 1：从 PDF 生成 DBC，再生成 C 注释

```bash
# 1. 提取 PDF 内容
uv run python ".github/skills/pdf-summary/scripts/extract_pdf.py" protocol.pdf --output outputs/protocol.txt

# 2. （人工或 AI）将 PDF 内容转换为 unified CSV
# 输出：outputs/protocol_unified.csv

# 3. 转换 CSV 为 DBC
uv run python ".github/skills/csv-to-dbc/scripts/csv2dbc.py" convert outputs/protocol_unified.csv -o outputs/protocol.dbc -e utf-8

# 4. 生成 C 注释 JSON
uv run python ".github/skills/dbc-to-comment/scripts/dbc2comment.py" convert outputs/protocol.dbc -e gb2312
```

### 场景 2：直接从现有 DBC 生成注释

```bash
# 如果已经有 DBC 文件
uv run python ".github/skills/dbc-to-comment/scripts/dbc2comment.py" convert existing_can_db.dbc -o can_comments.json -e gb2312
```

---

## 输出示例详解

### 信号类型 1：带描述的普通信号

**DBC 中的定义：**
```
SG_ Motor_Speed : 0|16@1+ (1.0,-15000.0) [-15000.0|15000.0] "rpm"  HCU
CM_ SG_ 217055237 Motor_Speed "电机转速正负表示电机转向，转速为正时与发动机正常转动方向一致";
```

**生成的 JSON：**
```json
{
    "Motor_Speed": "// Motor_Speed\t起始位:0\t长度:16\t系数:1\t偏移量:-15000\t单位:rpm\t电机转速正负表示电机转向，转速为正时与发动机正常转动方向一致"
}
```

### 信号类型 2：枚举型信号

**DBC 中的定义（JSON 格式注释）：**
```
SG_ Fail_Grade : 48|4@1+ (1.0,0.0) [0.0|3.0] ""  HCU
CM_ SG_ 217055237 Fail_Grade "{\"0\": \"No Fault\", \"1\": \"Warning(degraded)\", \"2\": \"Fault(zero torque output)\", \"3\": \"Fault(shut down MCU)\"}";
```

**生成的 JSON：**
```json
{
    "Fail_Grade": "// Fail_Grade\t起始位:48\t长度:4\t系数:1\t偏移量:0\t0:No Fault 1:Warning(degraded) 2:Fault(zero torque output) 3:Fault(shut down MCU)"
}
```

### 信号类型 3：无注释信号

**DBC 中的定义：**
```
SG_ Reserved : 52|12@1+ (1.0,0.0) [0.0|4095.0] ""  HCU
```

**生成的 JSON：**
```json
{
    "Reserved": "// Reserved\t起始位:52\t长度:12\t系数:1\t偏移量:0"
}
```

---

## 常见问题

### Q1: 中文乱码怎么办？

**A:** DBC 文件通常使用 GB2312 或 GBK 编码保存中文，使用 `-e gb2312` 参数：

```bash
uv run python ".github/skills/dbc-to-comment/scripts/dbc2comment.py" convert your.dbc -e gb2312
```

### Q2: 如何在 C 代码中使用生成的注释？

**A:** 可以编写脚本读取 JSON 并生成 C 头文件：

```python
import json

with open('comments.json', 'r', encoding='utf-8') as f:
    comments = json.load(f)

# 生成 C 头文件
with open('can_signals.h', 'w', encoding='utf-8') as f:
    for item in comments:
        for name, comment in item.items():
            f.write(f"{comment}\n")
            f.write(f"#define {name.upper()}_START_BIT ...\n\n")
```

### Q3: 支持哪些 DBC 版本？

**A:** 支持所有标准 DBC 格式，使用 cantools 库解析，兼容 Vector CANdb++ 等工具生成的 DBC。

### Q4: 如何提取特定消息的信号？

**A:** 当前版本提取所有信号。如需过滤，可以修改脚本或使用 jq 等工具过滤 JSON：

```bash
# 使用 jq 过滤包含 "Motor" 的信号
cat comments.json | jq '[.[] | select(keys[0] | contains("Motor"))]'
```

---

## 错误处理

### 错误 1: 文件不存在

```
✗ 文件不存在: xxx.dbc
```

**解决：** 检查 DBC 文件路径是否正确。

### 错误 2: DBC 解析失败

```
✗ 读取 DBC 文件失败: ...
```

**解决：**
1. 检查文件是否为有效的 DBC 格式
2. 尝试不同的编码：`-e utf-8` / `-e gb2312` / `-e gbk`
3. 使用 DBC 编辑器（如 Vector CANdb++）验证文件

### 错误 3: 编码错误

```
UnicodeDecodeError: 'utf-8' codec can't decode...
```

**解决：** 使用 `-e gb2312` 或 `-e gbk`：

```bash
uv run python ".github/skills/dbc-to-comment/scripts/dbc2comment.py" convert file.dbc -e gb2312
```

---

## 脚本技术细节

### 依赖库

- **cantools**: 解析 DBC 文件
- **typer**: 命令行界面
- **rich**: 美化终端输出

### 信号信息提取

从 DBC 的 `SG_` 定义中提取：
- `start`: 起始位
- `length`: 长度
- `scale`: 缩放系数
- `offset`: 偏移量
- `unit`: 单位
- `comment`: 注释（支持 JSON 格式）

### JSON 注释解析

如果信号注释是 JSON 格式：
- `{"description": "..."}` → 提取 description
- `{"0": "...", "1": "..."}` → 格式化为枚举值列表

---

## 版本信息

```bash
uv run python ".github/skills/dbc-to-comment/scripts/dbc2comment.py" version
```

输出：
```
DBC to C Comment JSON Generator v1.0.0
使用 cantools 库解析 DBC 文件
```

---

## 相关 Skills

- **csv-to-dbc**: 将 CSV 转换为 DBC 文件
- **pdf-to-can-csv**: 从 PDF 提取协议生成 CSV
- **pdf-summary**: 提取 PDF 内容

---

## 快速参考

```bash
# 最简单用法（自动命名输出）
uv run python ".github/skills/dbc-to-comment/scripts/dbc2comment.py" convert file.dbc

# 指定输出 + 中文编码
uv run python ".github/skills/dbc-to-comment/scripts/dbc2comment.py" convert file.dbc -o output.json -e gb2312

# 紧凑 JSON（2 空格缩进）
uv run python ".github/skills/dbc-to-comment/scripts/dbc2comment.py" convert file.dbc -i 2

# 不显示预览
uv run python ".github/skills/dbc-to-comment/scripts/dbc2comment.py" convert file.dbc --no-preview
```
