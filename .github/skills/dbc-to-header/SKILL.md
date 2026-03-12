# DBC to C Header - DBC转C头文件工具

## 描述

从 DBC (CAN数据库) 文件自动生成 C 语言头文件，包含完整的结构体定义、宏定义和联合体。支持位域自动拆分、预留位填充、64位总长度验证。

## 功能特性

### 核心功能
- ✅ **自动生成宏定义**：接收/发送消息数量、帧格式、波特率、ID定义、周期设置
- ✅ **智能结构体生成**：根据信号自动生成位域结构体
- ✅ **跨字节位域拆分**：自动将>8位信号拆分为 `_L` 和 `_H` 部分
- ✅ **预留位填充**：未定义的位自动填充为 `Res1`, `Res2`...
- ✅ **64位验证**：确保每个结构体总位数为64位（8字节）
- ✅ **联合体定义**：自动生成包含所有消息的 union
- ✅ **格式化注释**：保留枚举值和描述信息
- ✅ **参数验证**：波特率必须为 250 或 500，接收ID必须为十六进制格式
- ✅ **生成汇总**：自动显示波特率、接收/发送报文数量、周期、信号统计

### 代码风格
- 兼容嵌入式开发规范
- 字节边界注释 (`// Byte0`, `// Byte1`...)
- 对齐格式，可读性强
- 支持中英文混合注释

### 🔴 重要特性：接收ID参数决定消息分类

**⚠️ 关键行为：`--rx-id` 参数会重新定义消息的接收/发送分类**

- **指定 `--rx-id` 后，消息分类规则变更：**
  - ✅ ID 在 `--rx-id` 列表中的消息 → **接收消息**
  - ✅ ID 不在 `--rx-id` 列表中的消息 → **发送消息**
  - ⚠️ **原始 DBC 中的 sender 信息不再影响分类**

- **AI 使用建议：**
  1. 从需求文档/协议文档中提取接收帧 ID
  2. 将提取的 ID 通过 `--rx-id` 参数传入（可多次指定）
  3. 工具会自动将这些 ID 对应的消息标记为接收消息
  4. 其他所有消息自动标记为发送消息

**示例：**
```bash
# 文档中明确说明：MCU需要接收 0x0CFF09EF (HCU指令)
# 其他消息都是MCU发送的状态报文
uv run python scripts/dbc2header.py csv motor.csv \
    --baud 250 \
    --rx-id 0x0CFF09EF
# 结果：0x0CFF09EF → 接收消息，其他 → 发送消息
```

## 使用方法

### ⭐ 推荐方式：CSV 子命令（跳过 DBC 转换）

**优先使用此方式**，AI 可从需求文档中直接提取参数后生成头文件。

```bash
# 基本用法：从 CSV 生成 .h 文件
uv run python .github/skills/dbc-to-header/scripts/dbc2header.py csv \
    motor.csv \
    --baud 250 \
    --rx-id 0x0CFF09EF

# 指定输出文件
uv run python .github/skills/dbc-to-header/scripts/dbc2header.py csv \
    motor.csv \
    --baud 500 \
    --rx-id 0x0CFF09EF \
    --rx-id 0x18FF50E5 \
    -o motor.h
```

#### CSV 子命令参数说明

| 参数 | 类型 | 必需 | 说明 | 示例 |
|------|------|------|------|------|
| `CSV文件路径` | 位置参数 | ✅ | 输入的 CSV 文件路径 | `motor.csv` |
| `--baud, --baud-rate` | 选项 | ✅ | CAN 波特率（仅支持 250 或 500） | `--baud 250` |
| `--rx-id` | 选项 | ✅ | 接收帧 ID（十六进制格式，可多次指定） | `--rx-id 0x0CFF09EF` |
| `-o, --output` | 选项 | ❌ | 输出的 C 头文件路径（默认：`<csv名>.h`） | `-o motor.h` |
| `-p, --project` | 选项 | ❌ | 项目名称（默认：`Motor`） | `-p EVCU` |

**参数验证规则：**
- `--baud`：必须是 **250** 或 **500**，否则报错
- `--rx-id`：必须是十六进制格式（如 `0x0CFF09EF`、`0X1234`），否则报错
- 可以多次指定 `--rx-id` 来定义多个接收消息
- **🔴 接收报文数量不能为 0**：如果指定的 `--rx-id` 没有匹配到任何消息，会报错并显示可用的消息 ID
- **🔴 发送报文数量不能为 0**：如果所有消息都被指定为接收消息，会报错提示参数配置错误

**AI 使用提示：**
1. 从需求文档中提取 **波特率**（通常在通信矩阵或协议说明中）
2. 从需求文档中提取 **接收帧 ID**（MCU 需要接收的消息 ID）
3. 将提取的参数传入命令，工具会自动分类消息
4. 确保至少有 1 个接收消息和 1 个发送消息

---

### DBC 子命令（先转 CSV 再生成）

如果只有 DBC 文件，使用此方式（会先自动转换为 CSV）。

```bash
# 基本用法
uv run python .github/skills/dbc-to-header/scripts/dbc2header.py dbc \
    motor.dbc \
    --baud 250 \
    --rx-id 0x0CFF09EF

# 指定 DBC 编码
uv run python .github/skills/dbc-to-header/scripts/dbc2header.py dbc \
    motor.dbc \
    --baud 500 \
    --rx-id 0x0CFF09EF \
    -e gb2312 \
    -o motor.h
```

#### DBC 子命令参数说明

| 参数 | 类型 | 必需 | 说明 | 示例 |
|------|------|------|------|------|
| `DBC文件路径` | 位置参数 | ✅ | 输入的 DBC 文件路径 | `motor.dbc` |
| `--baud, --baud-rate` | 选项 | ✅ | CAN 波特率（仅支持 250 或 500） | `--baud 250` |
| `--rx-id` | 选项 | ✅ | 接收帧 ID（十六进制格式，可多次指定） | `--rx-id 0x0CFF09EF` |
| `-o, --output` | 选项 | ❌ | 输出的 .h 文件路径（默认：`<dbc名>.h`） | `-o motor.h` |
| `-e, --encoding` | 选项 | ❌ | DBC 文件编码（默认：`gb2312`） | `-e utf-8` |
| `-p, --project` | 选项 | ❌ | 项目名称（默认：`Motor`） | `-p EVCU` |

---

### 参数提取示例（AI 工作流程）

**场景：需求文档说明**
```
通信协议：CAN 2.0B 扩展帧
波特率：500Kbps
接收消息：
  - 0x0CFF09EF: HCU_Command（来自 HCU，周期 10ms）
  - 0x18FF50E5: BMS_Status（来自 BMS，周期 20ms）
发送消息：
  - 0x0CFF0009: MCU_Status1（发送至 HCU，周期 10ms）
  - ...
```

**AI 提取步骤：**
1. 波特率：`500` → `--baud 500`
2. 接收帧 ID：`0x0CFF09EF`, `0x18FF50E5` → `--rx-id 0x0CFF09EF --rx-id 0x18FF50E5`
3. 执行命令：
   ```bash
   uv run python scripts/dbc2header.py csv motor.csv \
       --baud 500 \
       --rx-id 0x0CFF09EF \
       --rx-id 0x18FF50E5 \
       -o motor.h
   ```

---

### 生成汇总示例

执行命令后会自动显示生成汇总：

```
                        生成汇总
┌──────────────────────┬──────────────────────────────────┐
│ 波特率               │ 500K                             │
│ 接收帧ID             │ 0x0CFF09EF, 0x18FF50E5           │
│ 接收报文             │ 2个                              │
│                      │   • 0x0CFF09EF HCU_Command       │
│                      │     (周期: 10ms)                 │
│                      │   • 0x18FF50E5 BMS_Status        │
│                      │     (周期: 20ms)                 │
│ 发送报文             │ 4个                              │
│                      │   • 0x0CFF0009 MCU_Status1       │
│                      │     (周期: 10ms)                 │
│                      │   • 0x0CFF0109 MCU_Status2       │
│                      │     (周期: 50ms)                 │
│                      │   • 0x0CFF0209 MCU_Status3       │
│                      │     (周期: 100ms)                │
│                      │   • 0x0CFF0309 MCU_Status4       │
│                      │     (周期: 100ms)                │
│ 接收信号             │ 16个                             │
│ 发送信号             │ 42个                             │
└──────────────────────┴──────────────────────────────────┘
```

---

### 旧版用法（不推荐，已弃用）

以下用法不再支持（缺少必需的 `--baud` 和 `--rx-id` 参数）：

```bash
# ❌ 已弃用：缺少波特率和接收ID参数
uv run python scripts/dbc2header.py motor.dbc

# ✅ 正确方式：必须指定参数
uv run python scripts/dbc2header.py dbc motor.dbc --baud 250 --rx-id 0x0CFF09EF
```

## 参数说明（旧版）

以下参数说明已过时，请参考上方的子命令参数说明。

## 输出示例

### 输入：GTAKE_motor_250K.dbc

包含以下消息：
- 1个接收消息：TM_HCU_Command (8字节，28个信号)
- 3个发送消息：TM_MCU_STATUS_1/2/3 (各8字节)

### 输出：GTAKE_motor_250K.h

```c
//*********************************** 宏定义 *********************************************//
//*********************************** CAN通讯接收数据帧个数 *********************************************//
#define SAE_MAX_RX_NUM  		1

//*********************************** CAN通讯发送数据帧个数 *******************************************//
#define SAE_MAX_TX_NUM  		3	//注意此处为协议定义发送个数,不用预留

//*********************************** CAN通讯数据帧格式 *********************************************//
#define EXIDEEN   				1   // 0:无效 1:使能扩展帧
#define STDIDEEN   				0   // 0:无效 1:使能标准帧

//*********************************** CAN通讯波特率设置 ***********************************************//
#define BAUD250					1   // 0:无效 1:250K波特率
#define BAUD500					0   // 0:无效 1:500K波特率

//******************************CAN通讯接收帧ID*******************************************//
#define CAN_ID_EVCU1 			((unsigned long)0x0CFF05EF)	// 接收VCU帧ID,ID=0x0CFF05EF

//*************************** CAN通讯发送数据帧周期(单位ms)*******************************//
#define MCUMSGTX0TIME			10	//报文发送周期
#define MCUMSGTX1TIME			50	//报文发送周期
#define MCUMSGTX2TIME			100	//报文发送周期

//*************************** CAN通讯数据帧结构体定义 ************************************//
// 接收报文1 :TM_HCU_Command
typedef struct __MOT_RX_APP1       
{
    // Byte0 ---------------------------------------------------
    unsigned TM_MCU_Enable         : 1; // 0:disable; 1:enable 
    unsigned TM_Fault_Reset        : 1; // 0:disable; 1:enable 
    unsigned TM_Control_Mode       : 2; // 0:Reserved; 1:Speed Control; 2:Torque Control; 3:Active Discharge 
    unsigned TM_Gear               : 2; // 0:Neutral; 1:Drive; 2:Reverse 
    unsigned TM_FootBrake          : 1; // 0:No FootBrake; 1:FootBrake 
    unsigned TM_HandBrake          : 1; // 0:No HandBrake; 1:HandBrake 
    // Byte1 ---------------------------------------------------
    unsigned TM_Demand_Limit_High_L: 8; // 转速指令限值上限，转矩控制模式时起作用 
    // Byte2 ---------------------------------------------------
    unsigned TM_Demand_Limit_High_H: 4; // 转速指令限值上限，转矩控制模式时起作用 
    unsigned TM_Demand_Limit_Low_L : 4; // 转速指令限值下限，转矩控制模式时起作用 
    // Byte3 ---------------------------------------------------
    unsigned TM_Demand_Limit_Low_H : 8; // 转速指令限值下限，转矩控制模式时起作用 
    // Byte4 ---------------------------------------------------
    unsigned TM_Demand_Torque_L    : 8; // 转矩的正负表示力的方向，发动机旋转方向为正向 
    // Byte5 ---------------------------------------------------
    unsigned TM_Demand_Torque_H    : 8; // 转矩的正负表示力的方向，发动机旋转方向为正向 
    // Byte6 ---------------------------------------------------
    unsigned TM_Demand_Speed_L     : 8; // 转速的正负表示电机旋转的方向，与发动机正常转动方向同向为正  
    // Byte7 ---------------------------------------------------
    unsigned TM_Demand_Speed_H     : 8; // 转速的正负表示电机旋转的方向，与发动机正常转动方向同向为正  


}TYPE_MOT_RX_APP1;

// 发送报文1：TM_MCU_STATUS_1
// ID = 0x0CFF0005
// T=10ms
typedef struct __MOTOR_TX1
{
    // Byte0 ---------------------------------------------------
    unsigned TM_Motor_Speed_L          : 8; // 电机转速正负表示电机转向 
    // Byte1 ---------------------------------------------------
    unsigned TM_Motor_Speed_H          : 8; // 电机转速正负表示电机转向 
    // Byte2 ---------------------------------------------------
    unsigned TM_Motor_Torque_L         : 8; // 扭矩大于0为转矩方向与发动机转向相同 
    // Byte3 ---------------------------------------------------
    unsigned TM_Motor_Torque_H         : 8; // 扭矩大于0为转矩方向与发动机转向相同 
    // Byte4 ---------------------------------------------------
    unsigned TM_Motor_AC_Current_L     : 8; // 交流侧电流有效值反馈 
    // Byte5 ---------------------------------------------------
    unsigned TM_Motor_AC_Current_H     : 8; // 交流侧电流有效值反馈 
    // Byte6 ---------------------------------------------------
    unsigned Res1                      : 4; // 预留 
    unsigned TM_Precharge_Allow        : 1; // 0:disable; 1:enable 
    unsigned TM_Active_Discharge_Enable: 1; // 0:disable; 1:enable 
    unsigned TM_IGBT_Enable_Feedback   : 1; // 0:disable; 1:enable 
    unsigned Res2                      : 1; // 预留 
    // Byte7 ---------------------------------------------------
    unsigned Res3                      : 4; // 预留 
    unsigned TM_Life_Counter_1         : 4; // 循环计数器  
}TYPE_MOT_TX1;

typedef union __SAE_DATA
{
	unsigned int WordArray[4];
	SAE_Bytes Bytes;
	TYPE_MOT_RX_APP1 MotRx1;  // TM_HCU_Command 
	TYPE_MOT_TX1 MotTx1; // TM_MCU_STATUS_1
	TYPE_MOT_TX2 MotTx2; // TM_MCU_STATUS_2
	TYPE_MOT_TX3 MotTx3; // TM_MCU_STATUS_3
}SAE_DATA;
```

## 技术细节

### 位域处理算法

#### 1. 跨字节拆分

对于超过8位的信号，自动拆分为低位和高位：

```
原始信号：TM_Demand_Limit_High (起始位=8, 长度=12位)

拆分结果：
- Byte1: TM_Demand_Limit_High_L : 8  // 低8位
- Byte2: TM_Demand_Limit_High_H : 4  // 高4位
```

#### 2. 预留位填充

对于DBC中未定义的位，自动填充预留字段：

```
信号1：bit 0-1 (2位)
信号2：bit 4-7 (4位)

自动填充：
- bit 2-3 → Res1 : 2  // 预留
```

#### 3. 64位验证

每个8字节结构体必须总计64位，如果不足会抛出错误：

```python
total_bits = sum(int(obj.bitLength) for obj in subList)
if total_bits != 64:
    raise ValueError(f"位数验证失败！总位数为 {total_bits}，应为 64 位")
```

### 消息分类

- **接收消息 (RX)**：sender为HCU/VCU/BMS → 生成 `TYPE_MOT_RX_APP<n>`
- **发送消息 (TX)**：sender为MCU/TM_MCU → 生成 `TYPE_MOTOR_TX<n>`

### ID格式处理

- **扩展帧**：ID > 0x7FF，使用8位十六进制 (如 `0x0CFF05EF`)
- **标准帧**：ID ≤ 0x7FF，使用3位十六进制 (如 `0x123`)
- **宏定义**：简化命名 `CAN_ID_EVCU1` 而非 `CAN_ID_TM_HCU_COMMAND`

## 典型工作流程

### 1️⃣ 从DBC直接生成头文件

```bash
# 一步到位
uv run python .github/skills/dbc-to-header/scripts/dbc2header.py \
    outputs/motor.dbc \
    -o src/can_protocol.h \
    -e gb2312
```

### 2️⃣ 验证生成的头文件

```bash
# 检查语法（使用C编译器）
gcc -fsyntax-only -std=c99 src/can_protocol.h

# 或者用于C++
g++ -fsyntax-only -std=c++11 src/can_protocol.h
```

### 3️⃣ 集成到项目

```c
// main.c
#include "can_protocol.h"

SAE_DATA can_rx_data;
SAE_DATA can_tx_data;

void process_can_message(uint32_t id, uint8_t* data) {
    if (id == CAN_ID_EVCU1) {
        memcpy(&can_rx_data.Bytes, data, 8);
        
        // 访问信号
        if (can_rx_data.MotRx1.TM_MCU_Enable) {
            // 电机使能
        }
        
        // 读取16位信号（自动组合_L和_H）
        uint16_t speed = (can_rx_data.MotRx1.TM_Demand_Speed_H << 8) | 
                         can_rx_data.MotRx1.TM_Demand_Speed_L;
    }
}
```

## 配合其他工具

### 与 csv-to-dbc 配合

```bash
# 流程：CSV → DBC → .h
uv run python .github/skills/csv-to-dbc/scripts/csv2dbc.py protocol.csv
uv run python .github/skills/dbc-to-header/scripts/dbc2header.py protocol.dbc
```

### 与 dbc-to-csv 配合验证

```bash
# 验证往返一致性
uv run python .github/skills/dbc-to-csv/scripts/dbc2csv.py motor.dbc -o temp.csv
uv run python scripts/compare_csv.py original.csv temp.csv
```

## 常见问题

### Q1: 生成的位域长度不是64怎么办？

**A:** 检查DBC文件中信号定义：
```bash
# 使用dbc2csv查看详细信息
uv run python .github/skills/dbc-to-csv/scripts/dbc2csv.py motor.dbc -o check.csv
```

常见原因：
- 信号起始位或长度定义错误
- 缺少某些信号
- 信号重叠

### Q2: 如何自定义ID宏名称？

**A:** 当前版本自动生成为 `EVCU1`, `EVCU2`...，如需自定义，可修改脚本中的命名逻辑：

```python
# 在 generate_header_file 函数中
macro_name = f"EVCU{idx}"  # 改为自定义名称
```

### Q3: 支持哪些DBC编码？

**A:** 常见编码都支持，常用的有：
- `utf-8`：国际标准
- `gb2312`：简体中文（默认）
- `gbk`：扩展简体中文
- `big5`：繁体中文
- `shift-jis`：日文

### Q4: 如何处理多行注释？

**A:** 工具会自动将DBC中的多行注释合并到单行，中文逗号和分号会保留。

## 错误处理

### 常见错误及解决方案

| 错误信息 | 原因 | 解决方案 |
|---------|------|---------|
| `位数验证失败！总位数为X，应为64位` | 信号总长度不等于8字节 | 检查DBC信号定义 |
| `DBC转换失败` | DBC文件格式错误或编码不匹配 | 尝试不同编码参数 `-e` |
| `找到 0 个消息` | DBC文件为空或解析失败 | 检查DBC文件有效性 |

### 调试模式

如果遇到问题，可以查看中间生成的CSV文件：

```bash
# 手动执行转换步骤
uv run python .github/skills/dbc-to-csv/scripts/dbc2csv.py motor.dbc -o debug.csv

# 查看CSV内容
cat debug.csv
```

## 性能说明

- **速度**：典型DBC文件（50个信号）< 1秒
- **内存**：峰值约50MB
- **文件大小**：生成的.h文件通常是DBC文件的2-3倍

## 依赖项

必需：
- `cantools`：DBC解析
- `typer`：命令行接口
- `rich`：终端美化输出

可选：
- `dbc-to-csv` skill（内部调用）

## 更新日志

### v1.0.0 (2026-03-12)
- ✅ 初始版本发布
- ✅ 支持位域自动拆分
- ✅ 预留位填充
- ✅ 64位验证
- ✅ 与原始controller.h格式完全兼容

## 相关Skills

- [csv-to-dbc](../csv-to-dbc/SKILL.md) - CSV转DBC
- [dbc-to-csv](../dbc-to-csv/SKILL.md) - DBC转CSV（本工具内部依赖）
- [dbc-to-comment](../dbc-to-comment/SKILL.md) - DBC转C注释JSON

## 快速参考

```bash
# 基础用法
uv run python .github/skills/dbc-to-header/scripts/dbc2header.py motor.dbc

# 完整参数
uv run python .github/skills/dbc-to-header/scripts/dbc2header.py motor.dbc -o motor.h -e gb2312

# 查看帮助
uv run python .github/skills/dbc-to-header/scripts/dbc2header.py --help
```

## 许可证

与主项目保持一致

## 作者

基于原始位域处理算法改进，集成DBC解析功能
