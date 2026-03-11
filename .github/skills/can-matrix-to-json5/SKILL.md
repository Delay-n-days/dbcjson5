---
name: can-matrix-to-json5
description: >
  将汽车 CAN/CAN FD 协议矩阵 Excel 文件（.xlsx）提取并转换为 JSON5 格式的报文定义。
  适用场景：用户上传 CAN Matrix xlsx 文件，并指定需要提取哪两个节点（如 VDCU 和 HVASAirPump）
  之间的通信报文，输出符合项目规范的 JSON5 代码。
  当用户提到 "CAN矩阵"、"报文提取"、"xlsx转json5"、"信号提取"、"DBC生成"、
  "节点间报文"、"CAN FD协议文件"、"Matrix sheet" 等关键词时，必须使用本 skill。
---

# CAN Matrix → JSON5 转换 Skill

## 任务概述

从汽车项目 CAN/CAN FD 协议矩阵 Excel 文件中，提取指定两个 **ECU 节点**之间交互的全部报文
和信号，输出标准化的 JSON5 格式定义代码。

---

## 第一步：理解输入

### 1.1 向用户确认以下信息（如未在对话中提及）

- **NODE1**（主控节点，如 `VDCU`、`VCU`、`BCM`）
- **NODE2**（目标节点，如 `HVASAirPump`、`MCU`、`BMS`）
- 如果用户只说"提取VDCU和HVAS之间的报文"，则 NODE1=VDCU，NODE2 视具体情况取 HVASAirPump 或 HVASOilPump 或 HVASDCDC24

---

## 第二步：读取 Excel 文件结构

### 2.1 探索 Sheet 列表

```python
import pandas as pd
xl = pd.ExcelFile("path/to/file.xlsx")
print(xl.sheet_names)
# 通常有: Cover, History, Legend, Matrix, CheckResult
```

### 2.2 读取 Matrix Sheet（不带 header，手动解析）

```python
df = pd.read_excel("path/to/file.xlsx", sheet_name="Matrix", header=None)
print(df.shape)       # 确认行列数
print(df.head(3))     # 预览前几行
```

> **重要**：必须使用 `header=None`，因为 Matrix 表格第 0 行是列标题，
> 但列标题本身包含换行符（如 `Msg Name\n报文名称`），直接用 header 会导致匹配失败。

### 2.3 确认关键列索引（第 0 行为表头行）

运行以下代码打印全部列名及其索引：

```python
for j in range(df.shape[1]):
    print(f"Col {j}: {str(df.iloc[0, j])}")
```

**DeepWay E2505 项目标准列索引映射**（其他项目请先探索确认）：

| 列索引 | 含义 |
|--------|------|
| 0  | Msg Name（报文名称）|
| 1  | Msg Type |
| 2  | Msg ID（报文标识符，如 `0x18FF5227x`）|
| 3  | PGN |
| 4  | Msg Send Type |
| 5  | Msg Cycle Time (ms) |
| 6  | Frame Format |
| 7  | BRS（传输速率切换标识位）|
| 8  | Msg Length / DLC（Byte）|
| 9  | Signal Name（信号名称）|
| 10 | Signal Description（信号描述，含中英文）|
| 11 | Byte Order |
| 12 | Start Byte |
| 13 | Start Bit（起始位）|
| 14 | SPN |
| 15 | Signal Send Type |
| 16 | Bit Length（信号长度）|
| 17 | Date Type（数据类型）|
| 18 | Resolution（精度/Factor）|
| 19 | Offset（偏移量）|
| 20 | Signal Min Value (phys)（物理最小值）|
| 21 | Signal Max Value (phys)（物理最大值）|
| 22 | Signal Min Value (Hex)（总线最小值）|
| 23 | Signal Max Value (Hex)（总线最大值）|
| 24 | Initial Value (Hex) |
| 25 | Invalid Value (Hex) |
| 26 | Error Value (Hex) |
| 27 | Inactive Value (Hex) |
| 28 | Unit（单位）|
| 29 | Signal Value Description |
| 30 | Remarks |
| 31 | Msg Cycle Time Fast (ms) |
| 32 | Msg Nr. Of Repetition |
| 33 | Msg Delay Time (ms) |
| 34 | GW_P |
| 35 | BDCU_P |
| **36** | **VDCU_P**（节点列，值为 S=发送 / R=接收）|
| 37 | TBOX_P |
| 38 | MCUF |
| 39 | MCUR |
| 40 | TCU |
| ... | ... |
| **50** | **HVASAirPump** |
| **51** | **HVASOilPump** |
| **52** | **HVASDCDC24** |
| 53 | DCDC24B |
| 54 | DCDC12 |

> **注意**：不同项目的节点列位置可能不同，必须先通过打印列名来确认正确索引。

---

## 第三步：筛选目标报文

### 3.1 筛选规则

一条报文被纳入输出，当且仅当：
- NODE1 的列值为 `S` 或 `R`（参与通信）
- NODE2 的列值为 `S` 或 `R`（参与通信）

即两个节点都出现在该报文的收发关系中。

### 3.2 判断 TX/RX 方向

- 若 NODE1 列 = `S`，NODE2 列 = `R` → TXNODE = NODE1，RXNODE = NODE2
- 若 NODE1 列 = `R`，NODE2 列 = `S` → TXNODE = NODE2，RXNODE = NODE1
- 若两者均为 `R`（均为接收方，说明有第三方节点发送）→ 根据报文名称前缀判断真正发送方，TXNODE 填该第三方节点名，RXNODE 可用两者中任意一个（或"Broadcast"），并在 COMMENT 中注明

### 3.3 MSGNAME 命名规则

按出现顺序编号：
- NODE1 发送的报文：`Rx{idx}_0x{ID}`（从 NODE2 视角是接收）
- NODE2 发送的报文：`Tx{idx}_0x{ID}`（从 NODE2 视角是发送）

> 即：以 NODE2 为视角，NODE2 接收的叫 Rx，NODE2 发送的叫 Tx。

---

## 第四步：解析每条报文的信号

### 4.1 表格行结构

Matrix 表格的行分为两类：

**报文行**（Message Row）：
- `row[0]` 非空，包含报文名称
- `row[2]` 包含报文 ID（如 `0x18FF5227x`，末尾有 `x` 需去除）
- `row[8]` 是 DLC（帧长度，字节）

**信号行**（Signal Row）：
- `row[0]` 为空（NaN）
- `row[9]` 非空，包含信号名称
- 其余信号属性在同行其他列

### 4.2 完整遍历逻辑

```python
messages = []
current_msg = None

for i, row in df.iterrows():
    if i == 0:
        continue  # 跳过表头行

    msg_name = row[0]
    if pd.notna(msg_name) and str(msg_name).strip() not in ['nan', '']:
        # 这是一个报文行
        vdcu_val = str(row[NODE1_COL]).strip() if pd.notna(row[NODE1_COL]) else ''
        node2_val = str(row[NODE2_COL]).strip() if pd.notna(row[NODE2_COL]) else ''
        
        current_msg = {
            'name': str(msg_name).strip(),
            'id_raw': str(row[2]).strip() if pd.notna(row[2]) else '',
            'dlc': int(row[8]) if pd.notna(row[8]) else 8,
            'node1_role': vdcu_val,
            'node2_role': node2_val,
            'relevant': (vdcu_val in ['S', 'R']) and (node2_val in ['S', 'R']),
            'sigs': []
        }
        messages.append(current_msg)

    sig_name = row[9]
    if pd.notna(sig_name) and str(sig_name).strip() not in ['nan', ''] and current_msg:
        # 这是一个信号行，读取信号属性
        current_msg['sigs'].append(parse_signal(row))
```

### 4.3 信号属性解析函数

```python
def parse_signal(row):
    def safe_int(val, default=0):
        try:
            return int(float(val)) if pd.notna(val) else default
        except:
            return default
    
    def safe_float(val, default=1.0):
        try:
            return float(val) if pd.notna(val) else default
        except:
            return default
    
    def safe_hex(val, default=0):
        """解析十六进制字符串，如 '0xFF' -> 255"""
        try:
            if pd.notna(val):
                s = str(val).strip()
                return int(s, 16)
            return default
        except:
            return default
    
    def safe_str(val):
        if pd.notna(val) and str(val).strip() not in ['nan', '']:
            return str(val).strip().replace('\n', ' ')
        return ''
    
    # Factor：精度。整数时输出整数，小数时保留原始精度
    factor = safe_float(row[18], 1.0)
    factor_out = int(factor) if factor == int(factor) else factor
    
    # Offset：偏移量。同上处理
    offset = safe_float(row[19], 0.0)
    offset_out = int(offset) if offset == int(offset) else offset
    
    # MIN/MAX 优先用 Hex 列（22/23），更准确
    # 物理值（20/21）受 factor/offset 影响，不适合直接作为总线值
    min_hex = safe_hex(row[22], 0)
    max_hex = safe_hex(row[23], 0)
    
    return {
        'name': safe_str(row[9]),
        'sbit': safe_int(row[13]),
        'len': safe_int(row[16]),
        'factor': factor_out,
        'offset': offset_out,
        'min': min_hex,
        'max': max_hex,
        'unit': safe_str(row[28]),
        'comment': safe_str(row[10]),
    }
```

---

## 第五步：生成 JSON5 输出

### 5.1 报文 ID 格式化

原始 ID 如 `0x18FF5227x`，需：
1. 去除末尾的 `x`
2. 解析为整数
3. 格式化为 `0x{8位大写十六进制}` 形式

```python
def format_id(raw_id_str):
    clean = raw_id_str.replace('x', '').replace('0x', '').replace('0X', '').strip()
    val = int(clean, 16)
    return f'0x{val:08X}'
```

### 5.2 JSON5 输出模板

```
{
    NODE1: "VDCU",
    NODE2: "HVASAirPump",
    MSGS: [
// +--------------------------------------------------------------------------------------------------------------------+
// | ID    MSGNAME   DLC  TXNODE   RXNODE   SIGS    SIG      SBIT   LEN      FACTOR  OFFSET  MIN   MAX    UINT  COMMENT |
// +--------------------------------------------------------------------------------------------------------------------+

    {ID: 0x18FF5227, MSGNAME: "Rx2_0x18FF5227", DLC: 8, TXNODE:"VDCU", RXNODE:"HVASAirPump", SIGS:[
        {SIG: "VDCU_HVASCmd_CRC      ",	SBIT: 0,	LEN: 8,	FACTOR: 1,  	OFFSET: 0,  	MIN: 0,  	MAX: 255,   	UINT:"",  	COMMENT: "CRC8"},
        {SIG: "VDCU_HVASCmd_AC       ",	SBIT: 8,	LEN: 4,	FACTOR: 1,  	OFFSET: 0,  	MIN: 0,  	MAX: 15,   	UINT:"",  	COMMENT: "Alive Counter"},
    ]},
// +--------------------------------------------------------------------------------------------------------------------+

    ]}
}
```

### 5.3 SIG 字段格式规范

- `SIG` 名称用空格补齐到固定宽度（建议 22 字符），用双引号包裹
- 各字段用 `\t`（Tab）分隔，保持对齐
- `FACTOR` 和 `OFFSET` 后跟两个空格加 `\t`（`  \t`）
- `MIN` 和 `MAX` 后跟两个空格加 `\t`（`  \t`）
- `UINT` 为空字符串时写 `""`，非空时写实际单位如 `"rpm"`、`"V"`、`"℃"`

```python
def format_sig_line(s):
    name_padded = s['name'].ljust(22)
    factor_str = str(s['factor'])
    offset_str = str(s['offset'])
    return (
        f'        {{SIG: "{name_padded}",\t'
        f'SBIT: {s["sbit"]},\t'
        f'LEN: {s["len"]},\t'
        f'FACTOR: {factor_str},  \t'
        f'OFFSET: {offset_str},  \t'
        f'MIN: {s["min"]},  \t'
        f'MAX: {s["max"]},   \t'
        f'UINT:"{s["unit"]}",  \t'
        f'COMMENT: "{s["comment"]}"}},')
```

---

## 第六步：常见陷阱与处理方法

### 6.1 ID 末尾有 `x` 字符

原始数据如 `0x18FF5227x`，转换时必须先去除末尾的 `x`：
```python
id_clean = raw.replace('x', '')  # 去除所有 x，包括前缀中的 0x 会被还原
# 更稳妥：
id_clean = raw.rstrip('x')  # 只去右侧的 x
```

### 6.2 Bit Length 列（col 16）可能读为字符串

某些行的 Bit Length 值被 pandas 读成字符串（如 `"Cycle"`），需用 `safe_int()` 防护：
```python
length = int(float(row[16])) if pd.notna(row[16]) else 0
# 如果 float() 失败，说明是文本，返回默认值 0
```

### 6.3 MIN/MAX 的选取策略

- **优先使用 Hex 列**（col 22/23：总线最小/最大值）作为 JSON5 中的 MIN/MAX
- 物理值列（col 20/21）是经过 factor/offset 换算后的工程值，不适合直接填入总线层定义
- Hex 列的值就是原始总线报文中的整数范围，如 `0x0` ~ `0xFFFF`

### 6.4 信号描述含换行符

Signal Description（col 10）经常包含 `\n`（中英文分行），输出到 COMMENT 时需替换为空格：
```python
desc = str(row[10]).replace('\n', ' ').strip()
```

### 6.5 NaN 值判断

用 `pd.notna(val)` 而不是 `val is not None`，因为 pandas 用 `float('nan')` 表示空单元格：
```python
# 正确
if pd.notna(row[9]) and str(row[9]).strip() not in ['nan', '']:
    ...
```

### 6.6 节点列值的变体

节点列的有效值通常为 `S`（发送）或 `R`（接收），但也可能出现：
- 空字符串 / NaN → 该节点不参与此报文
- `S/R`（极少数情况，网关节点）→ 同时发收

### 6.7 第三方节点广播报文

有些报文的 NODE1 和 NODE2 列均为 `R`，说明该报文由第三个节点发出，两者均接收。
处理方式：根据报文名前缀推断真实发送方（如 `MCUF_St1` 前缀 `MCUF` 即为 MCU Front），
TXNODE 填 `MCUF`，RXNODE 填两个接收方之一，并保留到输出中（通常保留）。

### 6.8 CANdb 符号长度超出了指定的最大限制！
CANdb symbol exceeds the specified maximum length!
一、什么时候会报这个错？
满足下面任意一种就会报错：
信号名（Signal name）太长
CANdb++ / DBC 对信号名有长度限制
一般限制：最多 31 或 32 个字符（不同版本略有差异）
报文名（Message name）太长
报文名字符数超过 DBC 文件格式上限
节点名、属性名、环境变量名等标识符过长
只要是 DBC 里的 ** 符号名称（Symbol）** 超长都会触发
你在这些操作时最容易遇到：
导入 Excel / 自动生成信号名（比如带很多下划线、前缀）
从 AUTOSAR、ARXML 转 DBC
批量修改变量名、复制粘贴长名称
二、最简单解决办法
把信号名、报文名改短，尽量：
英文 + 数字 + 下划线
总长度控制在 ≤31 个字符
去掉多余前缀、缩写长单词：
比如 Motor_Control_Status_Sensor1_Value
→ 改成 Motor_Stat_Sens1

---

## 第七步：输出与交付

1. 将 JSON5 内容保存至 `/mnt/user-data/outputs/` 目录，文件名格式：
   `{NODE1}_{NODE2}_CAN_Matrix.json5`

2. 调用 `present_files` 工具向用户提供下载链接

3. 附简要说明，包含：
   - 共提取多少条报文
   - 每条报文的 ID、名称、方向、信号数
   - 是否有第三方节点广播报文（如有，单独列出说明）

---

## 参考：完整 Python 转换脚本模板

见 `references/convert_script_template.py`

---

## 参考：JSON5 输出示例

见 `references/json5_output_example.json5`
