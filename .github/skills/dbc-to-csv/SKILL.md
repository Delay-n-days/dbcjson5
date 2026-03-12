---
name: dbc-to-csv
description: >
  从 DBC 文件反向生成统一 CSV 格式，实现 DBC ↔ CSV 双向转换。
  支持完整提取消息、信号、注释、枚举值等所有信息，转换为标准 Unified CSV 格式。
  适用场景：用户有 DBC 文件需要转换为 CSV 编辑；需要从 DBC 提取信号信息；
  或用户提到 "DBC转CSV"、"反向转换"、"DBC导出CSV"、"提取DBC信息"、
  "DBC to CSV"、"解析DBC文件" 等关键词时，必须使用本 skill。
  本 skill 内置 dbc2csv.py 脚本，无需用户额外上传转换工具。
---

# DBC → CSV 反向转换 Skill

## 任务概述

从标准 CAN DBC 文件中提取所有消息和信号信息，生成符合 Unified CSV 格式的表格文件。
支持完整的双向转换：CSV → DBC → CSV，确保数据完全可逆。

本 skill 内置 `dbc2csv.py` 脚本，使用 cantools 库解析 DBC 文件。

---

## 输出格式

生成的 CSV 文件包含 19 列标准格式：

```csv
消息ID,消息名称,消息长度,周期时间(ms),发送者,消息备注(JSON),信号名称,起始位,长度(bit),字节序,有符号,初值,缩放系数,偏移,最小值,最大值,单位,接收者,备注(JSON)
0x0CFF05EF,TM_HCU_Command,8,10,HCU,,TM_MCU_Enable,0,1,little_endian,否,,1,0,0,1,,TM_MCU,"{""0"": ""disable"", ""1"": ""enable""}"
```

**特点：**
- 消息ID：8位十六进制格式（扩展帧）
- 周期信息：从注释中自动提取
- JSON注释：枚举值和描述信息自动转换为 JSON 格式
- 数值格式：整数保持整数，浮点数保持浮点数
- 完全可逆：转换后的 CSV 可以无损还原为 DBC

---

## 使用方法

### 第一步：查看帮助

```bash
uv run python ".github/skills/dbc-to-csv/scripts/dbc2csv.py" --help
```

输出：
```
Usage: dbc2csv.py [OPTIONS] COMMAND [ARGS]...

  DBC 到 CSV 文件转换工具

Commands:
  convert  从 DBC 文件生成统一 CSV 格式
  version  显示版本信息
```

### 第二步：转换 DBC 文件

#### 基本用法（默认 GB2312 编码）

```bash
uv run python ".github/skills/dbc-to-csv/scripts/dbc2csv.py" convert <dbc文件>
```

**示例：**
```bash
uv run python ".github/skills/dbc-to-csv/scripts/dbc2csv.py" convert outputs/GTAKE_motor_250K.dbc
```

输出文件：`outputs/GTAKE_motor_250K_from_dbc.csv`（自动命名）

#### 指定输出文件

```bash
uv run python ".github/skills/dbc-to-csv/scripts/dbc2csv.py" convert <dbc文件> -o <输出csv>
```

**示例：**
```bash
uv run python ".github/skills/dbc-to-csv/scripts/dbc2csv.py" convert outputs/GTAKE_motor_250K.dbc -o outputs/motor.csv
```

#### 指定 DBC 文件编码

如果 DBC 文件是 UTF-8 编码：

```bash
uv run python ".github/skills/dbc-to-csv/scripts/dbc2csv.py" convert <dbc文件> -e utf-8
```

**示例：**
```bash
uv run python ".github/skills/dbc-to-csv/scripts/dbc2csv.py" convert outputs/protocol.dbc -o outputs/protocol.csv -e utf-8
```

---

## 命令参数说明

### convert 命令

| 参数 | 简写 | 类型 | 默认值 | 说明 |
|------|------|------|--------|------|
| `dbc_file` | - | 必填 | - | 输入的 DBC 文件路径 |
| `--output` | `-o` | 可选 | 自动生成 | 输出的 CSV 文件路径 |
| `--encoding` | `-e` | 可选 | `gb2312` | DBC 文件编码（utf-8/gb2312/gbk） |

---

## 典型工作流

### 场景 1：DBC 编辑工作流

```bash
# 1. 将 DBC 转换为 CSV
uv run python ".github/skills/dbc-to-csv/scripts/dbc2csv.py" convert motor.dbc -o motor.csv -e gb2312

# 2. 编辑 CSV 文件（使用 Excel 或文本编辑器）

# 3. 将修改后的 CSV 转回 DBC
uv run python ".github/skills/csv-to-dbc/scripts/csv2dbc.py" convert motor.csv -o motor_updated.dbc -e utf-8
```

### 场景 2：DBC 验证（双向转换测试）

```bash
# 1. DBC → CSV
uv run python ".github/skills/dbc-to-csv/scripts/dbc2csv.py" convert original.dbc -o test.csv -e gb2312

# 2. CSV → DBC
uv run python ".github/skills/csv-to-dbc/scripts/csv2dbc.py" convert test.csv -o recreated.dbc -e utf-8

# 3. 对比原始 CSV 和重新生成的 CSV
uv run python scripts/compare_csv.py compare original.csv test.csv
```

### 场景 3：批量提取多个 DBC 的信号信息

```bash
# 提取所有 DBC 文件的信号定义
for file in *.dbc; do
    uv run python ".github/skills/dbc-to-csv/scripts/dbc2csv.py" convert "$file" -e gb2312
done
```

---

## 注释转换规则

### 枚举值注释

**DBC 格式（数字枚举）：**
```
0 = Ready
1 = Running
2 = Fault
```

**转换为 JSON：**
```json
{"0": "Ready", "1": "Running", "2": "Fault"}
```

**DBC 格式（二进制枚举）：**
```
00:空档
01:前进档
10:后退档
```

**转换为 JSON：**
```json
{"00": "空档", "01": "前进档", "10": "后退档"}
```

### 描述性注释

**DBC 格式：**
```
电机转速正负表示电机转向
转速为正时与发动机正常转动方向一致
```

**转换为 JSON：**
```json
{"description": "电机转速正负表示电机转向\n转速为正时与发动机正常转动方向一致"}
```

### 混合注释（枚举 + 描述）

**DBC 格式：**
```
0 = No Fault
1 = Warning
故障等级说明
```

**转换为 JSON：**
```json
{"0": "No Fault", "1": "Warning", "description": "故障等级说明"}
```

---

## 周期信息提取

DBC 文件中的周期信息通常在消息注释中：

**DBC 注释：**
```
period 10ms
发送周期为10毫秒
```

**提取结果：**
- 周期时间(ms) 列：`10`
- 消息备注(JSON) 列：`{"description": "发送周期为10毫秒"}`

---

## 数据类型处理

### 整数 vs 浮点数

脚本智能识别数值类型：

| DBC 值 | CSV 输出 | 说明 |
|--------|---------|------|
| 1.0 | 1 | 整数值保持为整数 |
| 0.0 | 0 | 整数值保持为整数 |
| 0.1 | 0.1 | 浮点数保持为浮点数 |
| -5000.0 | -5000 | 整数值保持为整数 |

这确保了与原始 CSV 格式的完全一致性。

---

## 转换验证

### 使用对比工具验证

```bash
# 1. 转换 DBC 到 CSV
uv run python ".github/skills/dbc-to-csv/scripts/dbc2csv.py" convert test.dbc -o result.csv -e gb2312

# 2. 对比原始 CSV 和转换结果
uv run python scripts/compare_csv.py compare original.csv result.csv
```

**预期输出：**
```
✓ 两个文件完全一致（忽略了 0 列）
```

---

## 常见问题

### Q1: 中文乱码怎么办？

**A:** DBC 文件通常使用 GB2312 或 GBK 编码，使用 `-e gb2312` 参数（默认）：

```bash
uv run python ".github/skills/dbc-to-csv/scripts/dbc2csv.py" convert file.dbc -e gb2312
```

如果 DBC 是 UTF-8 编码，使用 `-e utf-8`。

### Q2: 如何保留所有信息？

**A:** 脚本自动提取所有信息：
- 消息ID、名称、长度
- 周期（从注释提取）
- 所有信号参数（起始位、长度、字节序、有符号、缩放、偏移、范围、单位）
- 注释（自动转换为 JSON 格式）

### Q3: 转换是否可逆？

**A:** 是的！转换完全可逆：

```bash
# CSV → DBC
uv run python ".github/skills/csv-to-dbc/scripts/csv2dbc.py" convert file.csv -o file.dbc

# DBC → CSV
uv run python ".github/skills/dbc-to-csv/scripts/dbc2csv.py" convert file.dbc -o file_back.csv

# 验证一致性
uv run python scripts/compare_csv.py compare file.csv file_back.csv
# 输出: ✓ 两个文件完全一致
```

### Q4: 支持扩展帧吗？

**A:** 完全支持！扩展帧 ID 自动格式化为 8 位十六进制：

- 标准帧：`0xCFF05EF` (11位)
- 扩展帧：`0x0CFF05EF` (29位)

### Q5: 如何处理没有注释的信号？

**A:** 注释列留空，不影响转换：

```csv
...,TM_Reserved,52,12,little_endian,否,,1,0,0,4095,,,
```

---

## 错误处理

### 错误 1: 文件不存在

```
错误: 文件 xxx.dbc 不存在
```

**解决：** 检查 DBC 文件路径是否正确。

### 错误 2: DBC 解析失败

```
转换错误: ...
```

**解决：**
1. 检查文件是否为有效的 DBC 格式
2. 尝试不同的编码：`-e utf-8` / `-e gb2312` / `-e gbk`
3. 使用 DBC 编辑器验证文件格式

### 错误 3: 编码错误

```
UnicodeDecodeError: 'gb2312' codec can't decode...
```

**解决：** 使用 `-e utf-8` 或 `-e gbk`：

```bash
uv run python ".github/skills/dbc-to-csv/scripts/dbc2csv.py" convert file.dbc -e utf-8
```

---

## 输出示例

### 完整示例

**输入 DBC：**
```dbc
BO_ 217055215 TM_HCU_Command: 8 HCU
 SG_ TM_MCU_Enable : 0|1@1+ (1,0) [0|1] "" TM_MCU
 SG_ TM_Control_Mode : 2|2@1+ (1,0) [0|3] "" TM_MCU

CM_ SG_ 217055215 TM_MCU_Enable "0 = disable
1 = enable";
CM_ SG_ 217055215 TM_Control_Mode "0 = Reserved
1 = Speed Control
2 = Torque Control
3 = Active Discharge";
CM_ BO_ 217055215 "period 10ms";
```

**输出 CSV：**
```csv
消息ID,消息名称,消息长度,周期时间(ms),发送者,消息备注(JSON),信号名称,起始位,长度(bit),字节序,有符号,初值,缩放系数,偏移,最小值,最大值,单位,接收者,备注(JSON)
0x0CFF05EF,TM_HCU_Command,8,10,HCU,,TM_MCU_Enable,0,1,little_endian,否,,1,0,0,1,,TM_MCU,"{""0"": ""disable"", ""1"": ""enable""}"
0x0CFF05EF,TM_HCU_Command,8,10,HCU,,TM_Control_Mode,2,2,little_endian,否,,1,0,0,3,,TM_MCU,"{""0"": ""Reserved"", ""1"": ""Speed Control"", ""2"": ""Torque Control"", ""3"": ""Active Discharge""}"
```

---

## 相关 Skills

- **csv-to-dbc**: 将 CSV 转换为 DBC 文件（反向转换）
- **dbc-to-comment**: 从 DBC 生成 C 语言注释
- **dbc-to-signals**: 从 DBC 生成信号定义列表

---

## 快速参考

```bash
# 最简单用法（自动命名输出）
uv run python ".github/skills/dbc-to-csv/scripts/dbc2csv.py" convert file.dbc

# 指定输出 + 编码
uv run python ".github/skills/dbc-to-csv/scripts/dbc2csv.py" convert file.dbc -o output.csv -e gb2312

# UTF-8 编码的 DBC
uv run python ".github/skills/dbc-to-csv/scripts/dbc2csv.py" convert file.dbc -e utf-8

# 版本信息
uv run python ".github/skills/dbc-to-csv/scripts/dbc2csv.py" version
```

---

## 版本信息

```bash
uv run python ".github/skills/dbc-to-csv/scripts/dbc2csv.py" version
```

输出：
```
dbc2csv v1.0
DBC 到 CSV 文件转换工具
```
