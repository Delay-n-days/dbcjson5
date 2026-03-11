---
name: pdf-to-can-csv
description: >
  将各种格式的 CAN 通讯协议文档转换为统一的 Unified CSV 格式（DBC 前置文件）。
  支持输入格式：PDF、Excel（.xlsx/.xls）、Word（.docx）、图片（.png/.jpg）、纯文本等。
  适用场景：用户上传任意格式的 CAN 协议文档，需要提取报文（Message）和信号（Signal）定义，
  生成可供 csv2dbc.py 使用的统一 CSV 表格。
  当用户提到 "协议转CSV"、"提取CAN报文"、"生成DBC前置文件"、"从文档提取信号"、
  "CAN通讯协议"、"电机控制器协议"、"MCU协议"、"VCU协议"、"扩展帧协议"、
  "报文定义提取"、"生成unified csv"、"协议文档转换" 等关键词时，必须使用本 skill。
---

# 协议文档 → Unified CSV 转换 Skill

## 任务概述

从任意格式的 CAN 通讯协议文档（PDF / Excel / Word / 图片 / 文本）中，
提取全部报文和信号定义 **不要编写任何脚本** ，输出符合 **Unified CSV 格式**的表格文件，
作为后续 `csv2dbc.py` 生成 DBC 文件的前置输入。
**注意必须附带完整的注释**

---

## 第一步：识别输入文件类型

文件位于 `/mnt/user-data/uploads/`，根据扩展名选择对应解析策略：

| 扩展名 | 类型 | 解析策略 |
|--------|------|----------|
| `.pdf` | PDF 文档 | Claude 直接视觉解析（无需工具） |
| `.xlsx` / `.xls` | Excel 表格 | pandas 读取，按表格结构提取 |
| `.docx` / `.doc` | Word 文档 | python-docx 或 pandoc 转文本后解析 |
| `.png` / `.jpg` / `.jpeg` | 图片截图 | Claude 视觉识别（OCR） |
| `.txt` / `.md` | 纯文本 | 直接文本解析 |
| `.csv` | 已有表格 | 直接映射到 Unified CSV 格式 |

```bash
ls /mnt/user-data/uploads/
```

---

## 第二步：按文件类型解析内容

### 2A. PDF 文件

#### 提取方式：使用 extract_pdf.py 生成 PDF 内容，然后由大模型处理

使用内置的 `extract_pdf.py` 工具从 PDF 提取所有文本和表格：

```bash
cd /home/claude/workspace
uv run python extract_pdf.py
```

此脚本输出 PDF 的完整文本内容和表格数据，然后 **由大模型（Claude）直接识别和处理**：

1. **无需编写脚本转换 PDF → CSV**，直接让大模型识别提取的内容
2. **大模型负责识别**：波特率、字节序、报文结构、信号定义
3. **大模型负责生成** Unified CSV 格式的表格内容
4. **避免错误**：绝不使用自动脚本生成 CSV，因为协议表格结构变异大，容易出错

#### 样例输出

严格按照 Unified CSV 格式输出，第一行是列名，后续每行一个信号：

```csv
消息ID,消息名称,消息长度,周期时间(ms),发送者,消息备注(JSON),信号名称,起始位,长度(bit),字节序,有符号,初值,缩放系数,偏移,最小值,最大值,单位,接收者,备注(JSON)
0x18FF5678,MCU2_STATUS5,8,,,,MCU1_VoltD,0,16,little_endian,否,,1,-30000,,,,,
0x18FF5678,MCU2_STATUS5,8,,,,MCU1_VoltQ,16,16,little_endian,否,,1,-30000,,,,,
0x1CFDD2F0,MCU2_STATUS4,8,,MCU2,,MCU2_Soft_ProtocolVer,8,4,little_endian,否,,0.1,2,,,,HCU,"{"0": "INIT", "1": "LV_PWR_UP", "2": "HV_PWR_UP", "3": "Idle", "4": "Speed Control", "5": "Torque Control", "6": "SHUTDWN(active capacitor discharge)", "7": 
0x1CFDD2F0,MCU2_STATUS4,8,,MCU2,,MCU2_Rotation_Unit,34,2,little_endian,否,,1,0,0,3,,HCU,
0x1CFDD2F0,MCU2_STATUS4,8,,MCU2,,MCU2_soft_ver,40,24,little_endian,否,,1,0,0,16777215,,HCU,"{"0": "INIT", "1": "LV_PWR_UP", "2": "HV_PWR_UP", "3": "Idle", "4": "Speed Control", "5": "Torque Control", "6": "SHUTDWN(active capacitor discharge)", "7": "LV_PWR_DWN", "8": "FAULT"}"
0x18FF42F0,MCU2_STATUS1,8,,MCU2,,MCU2_Speed,0,16,little_endian,否,,1,-6000,-6000,59535,rpm,HCU,"{"description": "电机转速正负表示电机转向，转速为正时与发动机正常转动方向一致"}"
0x18FF42F0,MCU2_STATUS1,8,,MCU2,,MCU2_Torque,16,16,little_endian,否,,1,-3200,-3200,62335,Nm,HCU,"{"description": "转矩矩大于0为转矩方向与发动机转向相同"}"
0x18FF42F0,MCU2_STATUS1,8,,MCU2,,MCU2_DC_Current,32,16,little_endian,否,,1,-1000,-1000,64535,A,HCU,
0x18FF42F0,MCU2_STATUS1,8,,MCU2,,MCU2_IvtPwmTzFrc,48,8,little_endian,否,,1,0,,,,,
0x18FF42F0,MCU2_STATUS1,8,,MCU2,,MCU2_Fail_Grade,56,4,little_endian,否,,1,0,0,15,,HCU,"{"0": "No Fault", "1": "Warning(degraded)", "2": "Fault(zero torque output)", "3": "Fault(shut down MCU)", "4": "Serious Fault(need to stop the vehicle)"}"
0x18FF42F0,MCU2_STATUS1,8,,MCU2,,MCU2_Work_Mode,60,4,little_endian,否,,1,0,0,15,,HCU,"{"0": "Ready（上电完成 MCU 已开管不 控制）", "1": "Enable（上电完成，MCU 未开管）", "2": "PowerUp（低压上电，准备上高压 或者高压上电过程中）", "3": "Error(错误)", "4": "防溜坡控制状态", "5": "转速模式扭矩受限", "6": "扭矩模式转速受限", "7": "快速下电中", "8": "扭矩控制", "9": "速度控制"}"
```
#### 读取pdf文件
**不要自己编写 PDF 解析脚本**，直接使用内置的 `epdf-summary` skill工具 ，它会提取 PDF 中的文本和表格内容

检查工作区是否有名为 `epdf-summary` 的skill，如果没有报错,否则利用 `extract_pdf.py` 提取 PDF 内容到 txt文件：然后读取txt文件内容，交给大模型处理：

```bash

#### 大模型处理流程

1. 运行 `extract_pdf.py` 获得完整的 PDF 文本和表格数据
2. 大模型读取输出结果
3. 大模型识别：
   - 波特率与字节序（如 `500kbps`，`INTEL 格式` = `little_endian`）
   - 报文列表表格（含 ID、名称、长度、周期）
   - 各报文的信号定义表格（含起始位、长度、参数名、范围、单位、偏移、比例）
   - 信号名称不得超过30个字符,注释使用json格式,尽量为中文
4. 大模型直接输出符合 Unified CSV 格式的表格内容（**不生成脚本**）


### 2B. Excel 文件（.xlsx）
优先使用大模型解析,如果大模型解析失败，再编写python脚本读取所有表格文本,然后交给大模型处理


```python
import pandas as pd
```

### 2C. Word 文件（.docx）
优先使用大模型解析,如果大模型解析失败，再编写python脚本读取所有文本,然后交给大模型处理

```bash
pip install python-docx --break-system-packages
python3 -c "
from docx import Document
doc = Document('/mnt/user-data/uploads/protocol.docx')

# 打印所有表格结构
for i, table in enumerate(doc.tables):
    print(f'=== 表格 {i} ({len(table.rows)}行 x {len(table.columns)}列) ===')
    for row in table.rows[:5]:
        print([cell.text.strip() for cell in row.cells])

# 打印段落（标题、注释）
for para in doc.paragraphs[:30]:
    if para.text.strip():
        print(para.text)
"
```

如 python-docx 不可用，尝试 pandoc：
```bash
pandoc /mnt/user-data/uploads/protocol.docx -t markdown -o /tmp/protocol.md && head -100 /tmp/protocol.md
```

### 2D. 图片文件（截图/拍照）
优先使用大模型解析,如果大模型解析失败，再编写python脚本读取所有文本,然后交给大模型处理
Claude 直接视觉识别图片中的表格内容：
- 识别表格行列结构及数值
- 提取十六进制 ID、数字参数、中英文混合内容
- 对模糊/不确定内容标注 `[unclear]` 并提示用户确认

### 2E. 纯文本 / Markdown
优先使用大模型解析,如果大模型解析失败，再编写python脚本
```bash
cat /mnt/user-data/uploads/protocol.txt | head -100
```

---

## 第三步：识别协议结构

无论何种输入格式，都需提取以下信息：

### 3.1 全局信息
- **波特率**：从协议文档开头提取，用于输出文件名后缀标注
- **字节序**：INTEL 格式 → `little_endian`；Motorola 格式 → `big_endian`
- **节点列表**：VCU、MCU、OilPump 等

#### 波特率识别规则

在文档中搜索以下关键词，提取波特率值：

| 文档中的写法 | 识别为 | 文件名后缀 |
|-------------|--------|-----------|
| `500kbps`、`500K`、`500 kbps` | 500K | `_500K` |
| `250kbps`、`250K`、`250 kbps` | 250K | `_250K` |
| `1Mbps`、`1000kbps`、`1M` | 1M | `_1M` |
| `125kbps`、`125K` | 125K | `_125K` |
| 未找到 / 不确定 | 未知 | `_UnknownBaud` |

> 若协议中存在**多个 CAN 通道且波特率不同**（如 CAN3=500K、CAN4=250K），
> 则按通道分别生成 CSV 文件，文件名各自加对应后缀。
> 若所有通道波特率相同，仅生成一个文件。

### 3.2 报文列表（每条报文）
- 消息 ID（十六进制，`0x0CFE05E4` 格式）
- 消息名称、长度（字节）、周期（ms）、发送方向

### 3.3 信号定义字段映射

| 协议字段 | CSV 列 | 处理规则 |
|----------|--------|----------|
| Start Bit | `起始位` | 整数 |
| Length(bit) | `长度(bit)` | 整数 |
| Parameter/Signal | `信号名称` | 加节点前缀确保唯一性 |
| Range `-15000~15000` | `最小值`/`最大值` | 解析范围字符串 |
| Unit | `单位` | rpm/Nm/A/V/degree Celsius |
| Offset | `偏移` | 浮点数 |
| Scale | `缩放系数` | 浮点数，默认 1 |
| Note/枚举值 | `备注(JSON)` | 转 JSON 格式 |

### 3.4 方向判断规则

```
报文名含 "VCU_To_XXX"  → 发送者=VCU，接收者=XXX_MCU
报文名含 "XXX_MCU_ST"  → 发送者=XXX_MCU，接收者=VCU
Note 含 "(VCU To MCU)" → 发送者=VCU
Note 含 "(MCU To VCU)" → 发送者=对应MCU
```

### 3.5 ID 复用处理

若协议说明"CAN3 中 X 的报文 ID 同 CAN4 中 Y"：
- 两者 ID 相同，消息名称不同
- 信号名称加节点前缀区分

---

## 第四步：构建 Unified CSV

### 4.1 19 列格式

```
消息ID,消息名称,消息长度,周期时间(ms),发送者,消息备注(JSON),
信号名称,起始位,长度(bit),字节序,有符号,初值,缩放系数,偏移,
最小值,最大值,单位,接收者,备注(JSON)
```

### 4.2 生成原则

- 每行一个信号，同一报文多行重复报文列
- 消息 ID 统一用 `0x` 前缀十六进制
- 信号名称全局唯一，加节点前缀
- JSON 字段内双引号转义为 `"`
- `有符号` 默认 `否`（用 offset 实现负值）

### 4.3 常见 scale/offset 参照

| 物理范围 | offset | scale |
|----------|--------|-------|
| -15000~15000 rpm | -15000 | 1 |
| -5000~5000 Nm | -5000 | 1 |
| -40~215 ℃ | -40 | 1 |
| 0~1000 A (AC) | 0 | 0.1 |
| -1000~1000 A (DC) | -1000 | 1 |
| 0~1000 V | 0 | 0.1 |

### 4.4 备注(JSON)列详细规则

**列位置**：第 19 列（最后一列）

**适用范围**：
- 消息级 `消息备注(JSON)`（第 6 列）
- 信号级 `备注(JSON)`（第 19 列）

#### 4.4.1 三种备注格式 不能共存

##### 格式 A：纯描述文字（推荐用于注释、说明）

```json
{"description": "电机转速正负表示电机转向"}
```

在 CSV 中的写法：
```csv
...,"{"description": "电机转速正负表示电机转向"}"
```

**应用场景**：
- 信号含义说明
- 注意事项警告
- 范围限制备注

**示例**：
```csv
0x0CFE05E4,VCU_To_OilPump_MCU_Cmd,8,10,VCU,{},Motor_Speed,0,16,little_endian,否,0,1,-15000,-15000,15000,rpm,OilPump_MCU,"{"description": "电机转速，负值表示反向转动"}ÿ
```

---

##### 格式 B：枚举型（十进制键，用于状态/故障码）

```json
{"0": "No Fault", "1": "Warning", "2": "Fault", "3": "Shutdown"}
```

在 CSV 中的写法：
```csv
...,"{"0": "No Fault", "1": "Warning", "2": "Fault", "3": "Shutdown"}"
```

**应用场景**：
- 故障状态枚举
- 工作模式枚举（0=待机、1=运行、2=停止）
- 任何有固定整数对应含义的信号

**示例**：
```csv
0x0CFE05E4,VCU_To_OilPump_MCU_Cmd,8,10,VCU,{},Fault_Level,16,2,little_endian,否,0,1,0,0,3,,OilPump_MCU,"{"0": "No Error", "1": "Warning", "2": "Serious Error", "3": "Shutdown"}"
```

**物理值→枚举映射**：
- 原始值 0 → "No Error"
- 原始值 1 → "Warning"
- 原始值 2 → "Serious Error"
- 原始值 3 → "Shutdown"

---

##### 格式 C：二进制枚举（用于位标志字段）

```json
{"00": "Neutral", "01": "Forward", "10": "Reverse", "11": "Reserved"}
```

在 CSV 中的写法：
```csv
...,"{"00": "Neutral", "01": "Forward", "10": "Reverse", "11": "Reserved"}"
```

**应用场景**：
- 档位枚举（0档、1档、2档用二进制表示）
- 多位标志位的含义（如 bit0=A状态、bit1=B状态）
- 多个离散状态的组合

**示例**：
```csv
0x0CFE05E4,VCU_To_OilPump_MCU_Cmd,8,10,VCU,{},Gear_Status,24,2,little_endian,否,0,1,0,0,3,,OilPump_MCU,"{"00": "空档位", "01": "前进档", "10": "后退档", "11": "无效"}"
```

---

#### 4.4.2 CSV 中 JSON 转义规则

在 CSV 文件中，JSON 字段需遵循以下规则：

| 内容 | 转义方式 | 示例 |
|------|--------|------|
| JSON 开始和结尾 | 用 `"` 双引号包裹整个字段 | `"{...}"` |
| JSON 内的双引号 | 转义为 `"` | `{"0": "No"}` → `{"0": "No"}` |
| JSON 内的反斜杠 | 保持不变 | `\"` 保持 `\"` |
| 换行符 | 不建议在 CSV 中使用，用 `\n` 转义 | `"line1\nline2"` |

**完整示例**（原始 JSON vs CSV 中的形式）：

原始 JSON：
```json
{"0": "No Fault", "1": "Warning"}
```

CSV 中的写法：
```csv
"{"0": "No Fault", "1": "Warning"}"
```

错误示例 ❌：
```csv
{"0": "No Fault", "1": "Warning"}
```
这样写会导致 CSV 解析错误，因为内部的引号会破坏 CSV 的列分隔。

---

#### 4.4.3 空值处理

| 情况 | 写法 | 说明 |
|------|------|------|
| 无备注 | `{}` 或留空 | 空 JSON 对象或完全空白 |
| 有 description | `"{"description": "xxx"}"` | 包含说明文字 |
| 有枚举 | `"{"0": "A", "1": "B"}"` | 包含状态映射 |

**示例**：
```csv
0x0CFE05E4,VCU_To_OilPump_MCU_Cmd,8,10,VCU,{},Signal1,0,16,little_endian,否,0,1,-15000,-15000,15000,rpm,OilPump_MCU,{}
0x0CFE05E4,VCU_To_OilPump_MCU_Cmd,8,10,VCU,{},Signal2,16,8,little_endian,否,0,1,0,0,255,,OilPump_MCU,"{"description": "备注内容"}"
```

---

#### 4.4.4 常见备注示例库

**电机类信号**：
```csv
"{"description": "电机转速，单位rpm，负值表示反向转动"}"
"{"description": "电机转矩，范围-5000~5000 Nm，偏移量-5000"}"
"{"0": "停止", "1": "正转", "2": "反转", "3": "故障"}"
```

**温度类信号**：
```csv
"{"description": "绕组温度，范围-40~215°C，偏移量-40"}"
"{"description": "温度传感器故障标志，0=正常，1=故障"}"
```

**故障类信号**：
```csv
"{"0": "无故障", "1": "警告", "2": "轻故障", "3": "重故障", "4": "关闭"}"
"{"description": "故障代码，详见故障代码表第3章"}"
```

**状态类信号**：
```csv
"{"00": "空档", "01": "D档", "10": "R档", "11": "P档"}"
"{"0": "离线", "1": "在线", "2": "初始化中", "3": "待命"}"
```

---

#### 4.4.5 验证与调试

**Python 验证脚本**：
```python
import json
import csv

def verify_json_field(csv_row):
    ""验证 CSV 行中的 JSON 字段是否合法""
    # 假设第 19 列是备注(JSON)
    json_field = csv_row[18]
    
    # 如果为空或 {}, 直接返回合法
    if not json_field or json_field == '{}':
        return True
    
    try:
        # 尝试解析（不需要额外转义，Python csv 库会自动处理）
        data = json.loads(json_field)
        print(f"✓ 合法 JSON: {json_field}")
        return True
    except json.JSONDecodeError as e:
        print(f"✗ 非法 JSON: {json_field}")
        print(f"  错误: {e}")
        return False

# 读取和验证
with open('output.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    for i, row in enumerate(reader, 1):
        if i == 1:  # 跳过表头
            continue
        verify_json_field(row)
```

---

## 第五步：CSV 生成（关键提示）

### ⚠️ 重要规则：**CSV 不能通过脚本自动生成，必须由大模型手动生成**

#### 为什么不能自动化？

1. **协议表格结构变异大**：不同厂商、不同协议版本的表格结构差异很大
2. **字段位置不固定**：信号参数在表格中的列顺序不统一
3. **嵌套和合并单元格**：许多协议文档使用合并单元格，自动解析容易出错
4. **中文关键词多样**：同一个概念有多种表述方式（如 "起始位"、"Start Bit"、"开始位置"）
5. **数据清理需人工判断**：格式错误、单位符号、范围解析等需要人工确认

#### 正确做法

1. **使用 extract_pdf.py（或 summarize_pdf.py）提取 PDF 内容**
   ```bash
   uv run python extract_pdf.py > pdf_content.txt
   ```

2. **大模型（Claude）读取提取的 PDF 内容**
   - 识别所有报文定义和信号参数
   - 解析数值范围、单位、偏移量、比例系数
   - 识别波特率、字节序、发送/接收方向

3. **大模型直接输出 Unified CSV 格式**
   - **不编写脚本来转换**
   - **不用自动化工具来解析**
   - 直接生成符合 19 列格式的表格文本
   - 所有 JSON 字段正确转义

4. **验证和保存**
   - 将大模型输出的 CSV 内容保存为文件
   - 编码：UTF-8
   - 第一行必须是列名（参考 4.1 节）
   - 每行一个信号，同一报文重复报文信息

#### 示例工作流

```bash
# 1. 提取 PDF
cd /home/claude/workspace
uv run python extract_pdf.py > outputs/protocol_extracted.txt

# 2. 大模型读取 protocol_extracted.txt，生成 CSV 文本
# （这一步在 Claude 对话中完成，不是脚本）

# 3. 保存大模型输出为 CSV 文件
cat > outputs/protocol_unified.csv << 'EOF'
消息ID,消息名称,消息长度,周期时间(ms),发送者,消息备注(JSON),信号名称,起始位,长度(bit),字节序,有符号,初值,缩放系数,偏移,最小值,最大值,单位,接收者,备注(JSON)
0x18ff31f0,VCU_COMMAND_IPU,8,10,VCU,"{}",Throttle_Pedal,0,7,little_endian,否,0,1,0,0,100,%,IPU,"{}"
...（其他行）
EOF

# 4. 验证 CSV 文件
ls -lh outputs/protocol_unified.csv
head -5 outputs/protocol_unified.csv

# 5. 转换为 DBC
uv run python csv2dbc.py convert outputs/protocol_unified.csv -o outputs/protocol.dbc -e utf-8
```

#### CSV 质量检查清单

- [ ] 列数必须是 19 列（没有多也没有少）
- [ ] 第一行是列名：`消息ID,消息名称,消息长度,...,备注(JSON)`
- [ ] 消息 ID 都以 `0x` 开头，使用十六进制
- [ ] 长度(bit) 都是整数（8, 16, 32 等）
- [ ] 缩放系数和偏移都是数字（可以是小数如 0.5）
- [ ] 有符号字段只能是 `"是"` 或 `"否"`
- [ ] JSON 字段双引号转义为 `"`，例如 `"{"key":"value"}"`
- [ ] 字节序只能是 `little_endian` 或 `big_endian`
- [ ] 各行的列数一致，没有缺少或多余的字段
- [ ] CSV 编码为 UTF-8（不是 GBK 或其他）

## 第五步：输出与验证

### 5.1 文件命名规则

**⚠️ 重要**：文件名必须包含波特率后缀，格式为：`{项目名}_{波特率}_unified.csv`

**波特率后缀映射表**：

| 协议中的波特率 | 文件名后缀 | 完整文件名示例 |
|-----------|---------|--------------|
| 250kbps、250K | `_250K` | `GTAKE_protocol_250K_unified.csv` |
| 500kbps、500K | `_500K` | `XugongMCU_500K_unified.csv` |
| 1Mbps、1000kbps | `_1M` | `ElectricMotor_1M_unified.csv` |
| 125kbps、125K | `_125K` | `LowSpeed_125K_unified.csv` |
| 未找到/不确定 | `_UnknownBaud` | `Protocol_UnknownBaud_unified.csv` |

**生成文件名的步骤**：
1. 从协议文档第一步提取的波特率值（如 "250kbps" → "250"）
2. 确定对应的后缀（"250" → "_250K"）
3. 项目名 + 波特率后缀 + "_unified.csv"

**Python 参考代码**：
```python
# 波特率后缀映射
BAUD_SUFFIX = {
    '500': '_500K',
    '250': '_250K',
    '1000': '_1M',
    '125': '_125K',
}

baud_kbps = "250"  # 从协议文档中提取
suffix = BAUD_SUFFIX.get(baud_kbps, '_UnknownBaud')

project_name = "GTAKE_protocol"
output_name = f"{project_name}{suffix}_unified.csv"
# 结果：GTAKE_protocol_250K_unified.csv
```

**多波特率通道示例**：
```
CAN3（500K）→ XugongMCU_CAN3_500K_unified.csv
CAN4（250K）→ XugongMCU_CAN4_250K_unified.csv
```

**保存位置**：`outputs/{项目名}_{波特率}_unified.csv`

### 5.2 自检清单

- [ ] ⚠️ **波特率已从文档中提取**，文件名包含正确的波特率后缀（如 `_250K`、`_500K`）
- [ ] 文件命名格式：`{项目名}_{波特率}_unified.csv`（例：`GTAKE_protocol_250K_unified.csv`）
- [ ] 报文数、信号数与原文档一致
- [ ] 同一报文内信号起始位不重叠
- [ ] 消息 ID 格式为 `0x` 十六进制
- [ ] JSON 双引号已转义 `"`
- [ ] 信号名称全局唯一

详细 CSV 格式规范见 `references/unified_csv_format.md`
