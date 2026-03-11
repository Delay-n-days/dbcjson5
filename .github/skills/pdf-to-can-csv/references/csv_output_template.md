# Unified CSV 输出模板与示例

## 文件信息

- **文件扩展名**：`.csv`
- **编码**：UTF-8（推荐）或 GB2312
- **分隔符**：逗号（`,`）
- **文本引号**：`"` 双引号（JSON 字段需转义）
- **行末**：CRLF（`\r\n`）或 LF（`\n`）

---

## 完整表头行

```csv
消息ID,消息名称,消息长度,周期时间(ms),发送者,消息备注(JSON),信号名称,起始位,长度(bit),字节序,有符号,初值,缩放系数,偏移,最小值,最大值,单位,接收者,备注(JSON)
```

**解释**：
- 列数：19 列
- 第 1-6 列：消息级别信息
- 第 7-19 列：信号级别信息
- 表头行必须在第一行

---

## 完整数据行示例

### 示例 1：简单电机转速信号

```csv
0x0CFE05E4,VCU_To_OilPump_MCU_Cmd,8,10,VCU,{},OilPump_Motor_Speed,0,16,little_endian,否,0,1,-15000,-15000,15000,rpm,OilPump_MCU,{}
```

**行解析**：
| 列号 | 列名 | 值 | 说明 |
|------|------|-----|------|
| 1 | 消息ID | `0x0CFE05E4` | 报文标识符（十六进制） |
| 2 | 消息名称 | `VCU_To_OilPump_MCU_Cmd` | CAN 报文名称 |
| 3 | 消息长度 | `8` | 8 字节 |
| 4 | 周期时间(ms) | `10` | 10 ms 发送一次 |
| 5 | 发送者 | `VCU` | VCU 节点发送 |
| 6 | 消息备注(JSON) | `{}` | 无备注 |
| 7 | 信号名称 | `OilPump_Motor_Speed` | 信号全局唯一名称 |
| 8 | 起始位 | `0` | 从字节 0 的第 0 位开始 |
| 9 | 长度(bit) | `16` | 信号占 16 比特 |
| 10 | 字节序 | `little_endian` | Intel 字节序 |
| 11 | 有符号 | `否` | 无符号 |
| 12 | 初值 | `0` | 初始值为 0 |
| 13 | 缩放系数 | `1` | 物理值 = 原始值 × 1 + ... |
| 14 | 偏移 | `-15000` | 物理值 = ... × 1 + (-15000) |
| 15 | 最小值 | `-15000` | 物理最小值 |
| 16 | 最大值 | `15000` | 物理最大值 |
| 17 | 单位 | `rpm` | 转速（转/分钟） |
| 18 | 接收者 | `OilPump_MCU` | 油泵 MCU 接收 |
| 19 | 备注(JSON) | `{}` | 无备注 |

---

### 示例 2：枚举型故障状态信号

```csv
0x0CFE05E4,VCU_To_OilPump_MCU_Cmd,8,10,VCU,{},Fault_Status,16,2,little_endian,否,0,1,0,0,3,,OilPump_MCU,"{""0"": ""No Fault"", ""1"": ""Warning"", ""2"": ""Fault"", ""3"": ""Shutdown""}"
```

**备注 JSON 说明**：
- 关键是第 19 列的 `备注(JSON)` 字段
- 原始 JSON：`{"0": "No Fault", "1": "Warning", "2": "Fault", "3": "Shutdown"}`
- CSV 中的转义形式：`{""0"": ""No Fault"", ""1"": ""Warning"", ""2"": ""Fault"", ""3"": ""Shutdown""}`
- 整个字段用 `"` 包裹

---

### 示例 3：温度信号（带偏移）

```csv
0x0CFE05EA,MCU_To_VCU_Feedback,8,20,MCU_1,{},Motor_Temp,0,8,little_endian,否,0,1,-40,-40,215,°C,VCU,"{""description"": ""电机绕组温度，范围 -40~215°C""}"
```

**物理值计算**：
- 原始值范围：0～255
- 物理值 = 原始值 × 1 + (-40)
- 原始值 0 → 物理值 -40°C
- 原始值 255 → 物理值 215°C

---

### 示例 4：同一消息的多个信号

```csv
0x18FF5678,MCU2_STATUS5,8,10,MCU_2,{},MCU1_VoltD,0,16,little_endian,否,,1,-30000,,,V,VCU,{}
0x18FF5678,MCU2_STATUS5,8,10,MCU_2,{},MCU1_VoltQ,16,16,little_endian,否,,1,-30000,,,V,VCU,{}
0x18FF5678,MCU2_STATUS5,8,10,MCU_2,{},MCU2_FreqCarries,32,8,little_endian,否,,0.1,0,,,kHz,VCU,{}
0x18FF5678,MCU2_STATUS5,8,10,MCU_2,{},MCU2_MLoopTime,40,8,little_endian,否,,1,0,,,ms,VCU,{}
```

**说明**：
- 同一消息 ID `0x18FF5678` 出现 4 次
- 每一行代表一个信号
- 消息级别的列（1-6）重复，信号级别的列（7-19）不同

---

### 示例 5：带描述备注的信号

```csv
0x0CFE05E4,VCU_To_OilPump_MCU_Cmd,8,10,VCU,{},Motor_Speed,0,16,little_endian,否,0,1,-15000,-15000,15000,rpm,OilPump_MCU,"{""description"": ""电机转速，负值表示反向转动。范围-15000~15000rpm""}"
```

---

## 生成 CSV 的 Python 示例代码

### 方法 1：使用 pandas 写入

```python
import pandas as pd

# 构建数据字典
data = {
    '消息ID': ['0x0CFE05E4', '0x0CFE05E4'],
    '消息名称': ['VCU_To_OilPump_MCU_Cmd', 'VCU_To_OilPump_MCU_Cmd'],
    '消息长度': [8, 8],
    '周期时间(ms)': [10, 10],
    '发送者': ['VCU', 'VCU'],
    '消息备注(JSON)': ['{}', '{}'],
    '信号名称': ['OilPump_Motor_Speed', 'Fault_Status'],
    '起始位': [0, 16],
    '长度(bit)': [16, 2],
    '字节序': ['little_endian', 'little_endian'],
    '有符号': ['否', '否'],
    '初值': [0, 0],
    '缩放系数': [1, 1],
    '偏移': [-15000, 0],
    '最小值': [-15000, 0],
    '最大值': [15000, 3],
    '单位': ['rpm', ''],
    '接收者': ['OilPump_MCU', 'OilPump_MCU'],
    '备注(JSON)': ['{}', '{"0": "No Fault", "1": "Warning", "2": "Fault", "3": "Shutdown"}'],
}

df = pd.DataFrame(data)

# 保存为 CSV（UTF-8 编码）
df.to_csv('output.csv', index=False, encoding='utf-8')

# 或使用 GBK 编码（Windows 兼容）
# df.to_csv('output.csv', index=False, encoding='gbk')
```

### 方法 2：手动写入 CSV 文件

```python
import csv
import json

rows = [
    {
        '消息ID': '0x0CFE05E4',
        '消息名称': 'VCU_To_OilPump_MCU_Cmd',
        '消息长度': 8,
        '周期时间(ms)': 10,
        '发送者': 'VCU',
        '消息备注(JSON)': {},
        '信号名称': 'OilPump_Motor_Speed',
        '起始位': 0,
        '长度(bit)': 16,
        '字节序': 'little_endian',
        '有符号': '否',
        '初值': 0,
        '缩放系数': 1,
        '偏移': -15000,
        '最小值': -15000,
        '最大值': 15000,
        '单位': 'rpm',
        '接收者': 'OilPump_MCU',
        '备注(JSON)': {},
    },
]

fieldnames = [
    '消息ID', '消息名称', '消息长度', '周期时间(ms)', '发送者', '消息备注(JSON)',
    '信号名称', '起始位', '长度(bit)', '字节序', '有符号', '初值', 
    '缩放系数', '偏移', '最小值', '最大值', '单位', '接收者', '备注(JSON)'
]

with open('output.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        # JSON 字段转字符串
        row['消息备注(JSON)'] = json.dumps(row['消息备注(JSON)'])
        row['备注(JSON)'] = json.dumps(row['备注(JSON)'])
        writer.writerow(row)
```

---

## 常见错误与检查清单

### ❌ 错误示例

**错误 1：JSON 字段未转义**
```csv
0x0CFE05E4,VCU_To_OilPump_MCU_Cmd,8,10,VCU,{},Fault_Status,16,2,little_endian,否,0,1,0,0,3,,OilPump_MCU,{"0": "No Fault"}
```
➜ 上方 CSV 解析会出错，因为 `"` 未转义

**正确**：
```csv
0x0CFE05E4,VCU_To_OilPump_MCU_Cmd,8,10,VCU,{},Fault_Status,16,2,little_endian,否,0,1,0,0,3,,OilPump_MCU,"{""0"": ""No Fault""}"
```

---

### ❌ 错误 2：消息 ID 格式不规范

**错误**：`CFE05E4` 或 `0xcfe05e4`（小写）
**正确**：`0x0CFE05E4` 或 `0x0cfe05e4`（保持一致）

---

### ❌ 错误 3：字节序拼写错误

**错误**：`Little_Endian` 或 `LITTLE_ENDIAN` 或 `Intel`
**正确**：`little_endian` 或 `big_endian`

---

## ✅ 检查清单

- [ ] 表头行准确无误，19 列齐全
- [ ] 消息 ID 格式为 `0x` + 8 位十六进制数字
- [ ] 字节序只使用 `little_endian` 或 `big_endian`（全小写）
- [ ] 有符号列只填 `是` 或 `否`
- [ ] JSON 字段内双引号已转义为 `""`
- [ ] 同一消息 ID 的多个信号信号起始位和长度不重叠
- [ ] 信号名称全局唯一（加节点前缀）
- [ ] 编码为 UTF-8 或 GBK（避免使用其他编码）
- [ ] 每行每列的数据类型符合规范（整数、浮点、枚举）
- [ ] 无多余的空白行
