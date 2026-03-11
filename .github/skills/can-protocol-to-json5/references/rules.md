# CAN 协议转换完整规则手册

## 目录
1. [信号字段解析规则](#1-信号字段解析规则)
2. [MIN/MAX 总线值换算](#2-minmax-总线值换算)
3. [保留位处理规则](#3-保留位处理规则)
4. [故障代码 Bit 展开规则](#4-故障代码-bit-展开规则)
5. [字节序处理规则](#5-字节序处理规则)
6. [信号命名规范](#6-信号命名规范)
7. [枚举值写法](#7-枚举值写法)
8. [多字节信号合并](#8-多字节信号合并)
9. [特殊信号类型处理](#9-特殊信号类型处理)
10. [CAN ID 推算与验证](#10-can-id-推算与验证)
11. [JSON5 格式细节](#11-json5-格式细节)

---

## 1 信号字段解析规则

### 1.1 协议 PDF 信号表标准列含义

| 列名（英文）| 列名（中文）| JSON5 字段 | 说明 |
|-----------|-----------|-----------|------|
| Start Bit | 起始位 | SBIT | Intel 格式为 LSB 位编号 |
| Length Bit | 位长度 | LEN | 信号占用的位数 |
| Signal | 信号名 | SIG | 英文名，用于 JSON5 SIG 字段 |
| Reference / 中文注释 | 信号描述 | COMMENT | 写入注释说明 |
| Scale / Resolution | 精度/分辨率 | FACTOR | 物理值 = 总线值 × FACTOR + OFFSET |
| Offset | 偏移量 | OFFSET | 可为负数（如温度 -40） |
| Unit | 单位 | UINT | V / A / ℃ / rpm / Hz / Nm / kW 等 |
| Min | 最小值 | MIN | **见第2节，填总线原始整数** |
| Max | 最大值 | MAX | **见第2节，填总线原始整数** |

### 1.2 信号行 JSON5 模板

```json5
{SIG: "NODE_SignalName          ",  SBIT: 0,  LEN: 16, FACTOR: 1,   OFFSET: 0,   MIN: 0, MAX: 1000, UINT:"V",  COMMENT: "英文描述 中文描述"},
```

格式要求：
- `SIG` 值补空格对齐到 **26 字符**（含引号）
- 字段间用 **Tab** 分隔
- `FACTOR`/`OFFSET` 为整数时写整数（`1` 不写 `1.0`）；小数保留原始精度（`0.1`、`0.01`）
- `COMMENT` 中英文混写，枚举值在此列出（见第7节）

---

## 2 MIN/MAX 总线值换算

### 2.1 换算公式

```
总线原始值（整数）= (物理值 - Offset) / Factor

MIN(总线) = (MIN(物理) - Offset) / Factor
MAX(总线) = (MAX(物理) - Offset) / Factor
```

### 2.2 常见换算示例

| 信号类型 | Factor | Offset | 物理范围 | 总线 MIN | 总线 MAX |
|---------|--------|--------|---------|---------|---------|
| 电压 0~1000V | 1 | 0 | 0~1000 V | 0 | 1000 |
| 电流 0~100A | 0.1 | 0 | 0~100 A | 0 | **1000** |
| 电流 0~200A | 0.01 | 0 | 0~200 A | 0 | **20000** |
| 温度 -40~210℃ | 1 | -40 | -40~210℃ | **0** | **250** |
| 温度 -40~215℃ | 1 | -40 | -40~215℃ | 0 | **255** |
| 转速 -15000~15000rpm | 1 | -15000 | -15000~15000 | 0 | **30000** |
| 转矩 -5000~5000Nm | 1 | -5000 | -5000~5000 | 0 | **10000** |
| 频率 0~600Hz | 0.01 | 0 | 0~600 Hz | 0 | **60000** |
| 转矩 0~500Nm | 1 | 0 | 0~500 | 0 | 500 |
| 功率 -500~500kW | 1 | -500 | -500~500 | 0 | **1000** |
| 里程 0~1500000kWh | 0.1 | 0 | 0~1500000 | 0 | **15000000** |
| 1bit 标志位 | 1 | 0 | 0~1 | 0 | 1 |
| 2bit 枚举 | 1 | 0 | 0~3 | 0 | 3 |
| 4bit 枚举 | 1 | 0 | 0~15 | 0 | 15 |

### 2.3 优先级

若协议文档同时给出：
- **物理值 Min/Max 列**（phys）
- **总线值 Min/Max 列**（hex/raw）

则**优先使用总线值列**；若只有物理值，按公式换算。

---

## 3 保留位处理规则

### 3.1 直接省略的信号特征

满足以下任一条件，**不写入 JSON5**：

| 特征 | 示例 |
|------|------|
| 信号名含关键字 | `Reserved`、`Retain`、`保留`、`预留`、`备用` |
| 信号名为空且文档标注保留 | 表格中描述列为"保留" |
| 固定填充位 | 文档说明"填0"或"填1"的固定位 |

### 3.2 省略后的注释说明

在报文注释行中说明跳过的保留位：

```json5
// [100ms] EHPS Status2 — 跳过: SBIT38~47(10bit保留), Byte3(8bit保留)
{ID: 0x1811A79B, MSGNAME: "Tx2_0x1811A79B", ...
```

### 3.3 不能省略的"功能性"信号

以下信号**必须保留**（尽管名字容易混淆）：

| 信号名 | 说明 |
|--------|------|
| `Live counter` / `Message Counter` / `Alive Rolling Counter` | 心跳帧，正常保留 |
| `DTC Code`（无 Bit 明细） | 故障码整体，保留为原始字段 |
| 固定校验码（如 `Check code`） | 协议规定的校验字段 |

---

## 4 故障代码 Bit 展开规则

### 4.1 判断是否展开

| 条件 | 处理方式 |
|------|---------|
| 文档有 Bit0~BitN 详细定义表 | **逐位展开**为独立 1bit 信号 |
| 仅描述"故障代码，见下表"但无 Bit 明细 | 保留为整体字节信号 |
| DTC Code（多字节故障码） | 有 Byte.Bit 明细时展开，无明细时整体保留 |

### 4.2 Bit → StartBit 换算（Intel 字节序）

```
StartBit = 该字节在帧中的起始位 + Bit序号

字节位置换算：
  Byte0 起始位 = 0
  Byte1 起始位 = 8
  Byte2 起始位 = 16
  Byte3 起始位 = 24
  Byte4 起始位 = 32
  Byte5 起始位 = 40
  Byte6 起始位 = 48
  Byte7 起始位 = 56

示例：故障代码在 Byte7（Start Bit=56）：
  Bit0 → SBIT = 56 + 0 = 56
  Bit1 → SBIT = 56 + 1 = 57
  Bit2 → SBIT = 56 + 2 = 58
  Bit3 → SBIT = 56 + 3 = 59  （若标注"不可查询" → 省略）
  Bit4 → SBIT = 56 + 4 = 60
  Bit5 → SBIT = 56 + 5 = 61
  Bit6 → SBIT = 56 + 6 = 62
  Bit7 → SBIT = 56 + 7 = 63

示例：DTC Code 从 SBIT=0（Byte1.bit0 ~ Byte2.bit7）：
  Byte1 Bit0 → SBIT = 0
  Byte1 Bit1 → SBIT = 1
  Byte2 Bit0 → SBIT = 8
  Byte2 Bit1 → SBIT = 9
```

### 4.3 展开后信号格式

```json5
// 故障代码 Byte7(SBIT=56) 逐位展开，Bit3(不可查询)已省略
{SIG: "EHPS_FaultUnderVolt      ",  SBIT: 56, LEN: 1, FACTOR: 1, OFFSET: 0, MIN: 0, MAX: 1, UINT:"", COMMENT: "输入欠压故障 0=正常 1=故障"},
{SIG: "EHPS_FaultOverVolt       ",  SBIT: 57, LEN: 1, FACTOR: 1, OFFSET: 0, MIN: 0, MAX: 1, UINT:"", COMMENT: "输入过压故障 0=正常 1=故障"},
{SIG: "EHPS_FaultLVPower        ",  SBIT: 58, LEN: 1, FACTOR: 1, OFFSET: 0, MIN: 0, MAX: 1, UINT:"", COMMENT: "低压电源故障 0=正常 1=故障"},
// SBIT=59 (Bit3): 文档注明"此位不能查询" → 省略
{SIG: "EHPS_FaultOverHeat       ",  SBIT: 60, LEN: 1, FACTOR: 1, OFFSET: 0, MIN: 0, MAX: 1, UINT:"", COMMENT: "过热故障 0=正常 1=故障"},
{SIG: "EHPS_FaultShortCkt       ",  SBIT: 61, LEN: 1, FACTOR: 1, OFFSET: 0, MIN: 0, MAX: 1, UINT:"", COMMENT: "短路故障 0=正常 1=故障"},
{SIG: "EHPS_FaultOverLoad       ",  SBIT: 62, LEN: 1, FACTOR: 1, OFFSET: 0, MIN: 0, MAX: 1, UINT:"", COMMENT: "过载故障 0=正常 1=故障"},
{SIG: "EHPS_FaultPhaseLoss      ",  SBIT: 63, LEN: 1, FACTOR: 1, OFFSET: 0, MIN: 0, MAX: 1, UINT:"", COMMENT: "缺相故障 0=正常 1=故障"},
```

### 4.4 多字节 DTC（如 MCU STATUS 3/7 中的故障码）

MCU 协议中 DTC 按 Byte.bit 组织，展开方式相同：

```json5
// DTC Byte1(SBIT=0) 展开
{SIG: "MCU_FaultOverVolt        ",  SBIT: 0,  LEN: 1, FACTOR: 1, OFFSET: 0, MIN: 0, MAX: 1, UINT:"", COMMENT: "Over Voltage Error 过压故障 Grade=3"},
{SIG: "MCU_FaultOverCurr        ",  SBIT: 1,  LEN: 1, FACTOR: 1, OFFSET: 0, MIN: 0, MAX: 1, UINT:"", COMMENT: "Over Current Error 过流故障 Grade=3"},
// DTC Byte2(SBIT=8) 展开
{SIG: "MCU_FaultIPM             ",  SBIT: 8,  LEN: 1, FACTOR: 1, OFFSET: 0, MIN: 0, MAX: 1, UINT:"", COMMENT: "IPM Error 硬件故障 Grade=4"},
```

---

## 5 字节序处理规则

### 5.1 默认 Intel（小端）

协议文档默认格式为 **Intel（小端）**，低字节在前，高字节在后。
StartBit = **LSB（最低有效位）** 的位编号。

### 5.2 Motorola（大端）特例

仅在文档明确注明 `Motorola` 时处理，如：
- 绝缘检测仪 ICU 报文 `0x1819A1A4`
- 霍尔电流传感器报文

处理方式：
1. 在报文注释行加 `// ⚠️ Motorola 格式`
2. SBIT 按文档原始值填写（Motorola 定义的 MSB 位编号）
3. 在 COMMENT 中注明 `[Motorola]`

```json5
// ⚠️ Motorola 格式（文档注明）
{ID: 0x1819A1A4, MSGNAME: "Rx0_0x1819A1A4", DLC: 8, TXNODE:"ICU", RXNODE:"VCU", SIGS:[
    {SIG: "ICU_InsulResistance      ",  SBIT: 8,  LEN: 16, FACTOR: 1,   OFFSET: 0, MIN: 0, MAX: 65535, UINT:"kΩ", COMMENT: "[Motorola] Insulation resistance 绝缘电阻"},
```

---

## 6 信号命名规范

### 6.1 命名格式

```
{节点缩写}_{功能描述}[_{细分}]

长度建议：≤ 26 字符（JSON5 中补空格对齐用）
```

### 6.2 常用命名模式

| 场景 | 命名示例 |
|------|---------|
| 普通模拟量 | `EHPS_InputVolt` / `MCU_MotorSpeed` |
| 多相信号 | `EHPS_OutU_Volt` / `EHPS_OutV_Curr` / `EHPS_OutW_Volt` |
| 状态枚举 | `EHPS_DcAcStatus` / `MCU_WorkMode` / `MCU_CtrlMode` |
| 故障等级 | `EHPS_FaultGrade` / `MCU_FailGrade` |
| 故障位（展开）| `EHPS_FaultUnderVolt` / `MCU_FaultOverVolt` / `MCU_FaultIPM` |
| 控制指令 | `VCU_OilPump_CtrlCmd` / `VCU_Neg_ContCtrl` |
| 接触器状态 | `HVB_PosContSt` / `HVB_NegContSt` |
| 心跳帧 | `EHPS_LiveCounter` / `MCU_LiveCounter` |
| 使能反馈 | `MCU_IGBTEnableFB` / `MCU_ActiveDischFB` |

### 6.3 禁止事项

- ❌ 名称超过 30 字符（影响对齐）
- ❌ 含空格或特殊字符
- ❌ 直接使用中文
- ❌ 和其他信号重名（同一 JSON5 文件内唯一）

---

## 7 枚举值写法

有枚举定义的信号，全部列举到 COMMENT 中：

```json5
// 简单枚举（≤4 个值）
COMMENT: "DC/AC pump status 0=停机 1=预充电中 2=预充电完成 3=运行"

// 较多枚举（≤8 个值）
COMMENT: "Work Mode 工作状态 0=INIT 1=LV_PWR_UP 2=预留 3=Idle 4=速度控制 5=转矩控制 6=主动放电 7=LV_PWR_DWN 8=FAULT"

// 带条件枚举（如 Not Available）
COMMENT: "Vehicle Status 整车状态 0=关闭 1=ON档 2=READY 3=Not Available"

// 故障等级（固定格式）
COMMENT: "Fault grade 故障等级 0=无故障 1=一级(警告降额) 2=二级(零转矩) 3=三级(关断重启) 4=四级(停车)"
```

**MIN/MAX 不受枚举影响**：枚举信号的 MIN/MAX 仍填总线有效整数范围（如 0~3、0~15）。

---

## 8 多字节信号合并

### 8.1 合并规则

文档中若将同一信号分"高字节"/"低字节"分别描述，**合并为单一信号**：

```
Byte3 = Output current 低字节  (SBIT=24)
Byte4 = Output current 高字节  (SBIT=32)
→ 合并：SBIT=24, LEN=16
```

### 8.2 32bit 信号（4字节）

```
Byte1~4 = VehTotDst 总里程（32bit）
→ SBIT=0（或文档给出的起始位）, LEN=32
```

### 8.3 特殊：霍尔传感器电流（符号扩展）

霍尔传感器 IP_VALUE 为 32bit 有符号，0x80000000=0mA：

```json5
{SIG: "HALL_IP_Value            ",  SBIT: 24, LEN: 32, FACTOR: 0.001, OFFSET: -2147483.648, MIN: 0, MAX: 4294967295, UINT:"A", COMMENT: "直流电流 0x80000000=0mA 0x7FFFFFFF=-1mA 0x80000001=1mA"},
```

---

## 9 特殊信号类型处理

### 9.1 开关机指令字节（0xAA / 0x55）

```json5
{SIG: "VCU_OilPump_CtrlCmd      ",  SBIT: 0, LEN: 8, FACTOR: 1, OFFSET: 0, MIN: 0, MAX: 255, UINT:"", COMMENT: "Oil pump enable 0xAA=开机 0x55=关机"},
```

### 9.2 生命帧（心跳计数器）

```json5
{SIG: "MCU_LiveCounter          ",  SBIT: 60, LEN: 4, FACTOR: 1, OFFSET: 0, MIN: 0, MAX: 15, UINT:"", COMMENT: "Live counter 循环计数器 0~15"},
{SIG: "HVB_MsgCounter           ",  SBIT: 56, LEN: 4, FACTOR: 1, OFFSET: 0, MIN: 0, MAX: 15, UINT:"", COMMENT: "Message Counter 心跳信号 0~15循环"},
```

### 9.3 绝缘检测仪固定状态字节（0xAA/0x55 含义）

```json5
{SIG: "ICU_WorkMode             ",  SBIT: 40, LEN: 8, FACTOR: 1, OFFSET: 0, MIN: 0, MAX: 255, UINT:"", COMMENT: "运行状态 0xAA=正常运行 0x55=绝缘功能关闭"},
{SIG: "ICU_AlarmMode            ",  SBIT: 48, LEN: 8, FACTOR: 1, OFFSET: 0, MIN: 0, MAX: 255, UINT:"", COMMENT: "报警状态 0xAA=无绝缘故障 0x55=有绝缘故障"},
```

### 9.4 MSD 高压互锁信号

```json5
{SIG: "HVB_MSD1_Interlock       ",  SBIT: 28, LEN: 2, FACTOR: 1, OFFSET: 0, MIN: 0, MAX: 1, UINT:"", COMMENT: "MSD1高压互锁信号 0=断开 1=连接"},
```

### 9.5 故障指示灯（DM1）

DM1 报文中的指示灯字节按 2bit 一组展开：

```json5
{SIG: "XXX_FaultIndicator       ",  SBIT: 6, LEN: 2, FACTOR: 1, OFFSET: 0, MIN: 0, MAX: 1, UINT:"", COMMENT: "故障指示灯 0=灭 1=亮 (Bit7~6)"},
{SIG: "XXX_RedStopLamp          ",  SBIT: 4, LEN: 2, FACTOR: 1, OFFSET: 0, MIN: 0, MAX: 1, UINT:"", COMMENT: "红色停止灯 0=灭 1=亮 (Bit6~5)"},
{SIG: "XXX_AmberWarnLamp        ",  SBIT: 2, LEN: 2, FACTOR: 1, OFFSET: 0, MIN: 0, MAX: 1, UINT:"", COMMENT: "琥珀色警告灯 0=灭 1=亮 (Bit4~3)"},
{SIG: "XXX_YellowProtLamp       ",  SBIT: 0, LEN: 2, FACTOR: 1, OFFSET: 0, MIN: 0, MAX: 1, UINT:"", COMMENT: "黄色保护灯 0=灭 1=亮 (Bit2~1)"},
```

---

## 10 CAN ID 推算与验证

### 10.1 SAE J1939 29位 ID 结构

```
Bit[28:26] Priority (3bit)
Bit[25]    Reserved (通常0)
Bit[24]    Data Page
Bit[23:16] PDU Format (PF)
Bit[15:8]  PDU Specific (PS) / Destination
Bit[7:0]   Source Address (SA)

简化公式：
CAN_ID = (Priority << 26) | (PGN << 8) | SourceAddress
```

### 10.2 验证示例

```
报文：Priority=0x6, PGN=0x01A7, SA=0x9B (EHPS)
→ (6 << 26) = 0x18000000
→ (0x01A7 << 8) = 0x0001A700
→ SA = 0x9B
→ ID = 0x18000000 | 0x0001A700 | 0x9B = 0x1801A79B ✓

报文：Priority=0x3, PGN=0xFF08, SA=0xEF (VCU)
→ (3 << 26) = 0x0C000000
→ (0xFF08 << 8) = 0x00FF0800
→ SA = 0xEF
→ ID = 0x0C000000 | 0x00FF0800 | 0xEF = 0x0CFF08EF ✓
```

---

## 11 JSON5 格式细节

### 11.1 信号名对齐

SIG 字段值（含双引号）补空格至 28 字符：

```python
name_pad = signal_name.ljust(26)  # 26字符内容 + 2个引号 = 28
f'SIG: "{name_pad}"'
```

### 11.2 分隔符

字段间统一用 **Tab (`\t`)** 分隔，不用空格。

### 11.3 FACTOR/OFFSET 格式

```
整数：写 1、0、-40、-5000（不写 1.0、0.0）
小数：写 0.1、0.01、0.001、0.00390625（按文档精度）
```

### 11.4 报文注释行

```json5
// [发送周期ms] 报文功能描述（发送方→接收方）[字节序注意事项]
```

### 11.5 分隔线

每条报文前后用分隔线隔开：

```
// +------------------------------------------------------------------------+
```

### 11.6 文件头注释

```json5
{
    // 节点 XX（缩写）CAN 报文定义 — 含故障位展开，已省略所有保留位
    // 来源：协议文档名称及版本 第X.X节
    // 协议：SAE J1939，CAN 2.0B，29位扩展帧，250Kbs，Intel字节序（默认）
    // 节点地址：NODE1=0xXX(DEC)  NODE2=0xXX(DEC)
    // 统计：共N条报文(MRx+NTx)，M个信号，故障位展开N个
    
    NODE1: "VCU",
    NODE2: "EHPS",
    MSGS: [
```
