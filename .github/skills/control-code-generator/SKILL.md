# Control Code Generator - 控制器代码生成器

---
name: control-code-generator
description: >
    从 CAN 协议 CSV 自动生成控制器完整代码（.h 头文件 + .c 源文件）。自动化流程包括：使用 dbc-to-header 生成协议头文件，由 AI 分析协议并提取配置，使用 csv-to-source 生成接收解析代码。
    适用场景：用户需要生成完整的控制器代码；或用户提到 "CSV 转控制器代码"、"生成控制器 C 和 H 文件"、"CAN 协议控制器代码生成"、"完整代码生成" 等关键词时，必须使用本 skill。
    本 skill 整合了 dbc-to-header 和 csv-to-source 两个 skill，提供一站式代码生成服务。
---

## 🎯 核心功能

从 **CAN 协议 CSV 文件** 自动生成控制器完整代码，包括：
- **协议头文件 (.h)**：完整的结构体定义、宏定义、联合体
- **接收解析代码 (.c)**：`SaeRxUpdateVar` 函数的实现代码片段

---

## 📋 生成流程

### 整体流程图

```
CSV 协议文件
    ↓
┌─────────────────────────────────────────────────────────┐
│ Step 1: 生成协议头文件 (.h)                               │
│ 工具: dbc-to-header skill                                │
│ 输入: CSV + 波特率 + 接收帧ID                             │
│ 输出: 完整的协议头文件 (结构体、宏定义、联合体)            │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│ Step 2: AI 分析并提取配置                                 │
│ 方式: 由大模型分析 CSV + .h 文件                          │
│ 任务: 提取接收消息的结构体名称 (TYPE_MOT_RX_APPx)         │
│       建立信号与输出变量的映射关系                         │
│ 输出: config.json 配置文件                                │
│ ⚠️ 注意: 此步骤不使用脚本，由 AI 人工分析生成              │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│ Step 3: 生成接收解析代码 (.c)                             │
│ 工具: csv-to-source skill                                │
│ 输入: config.json + CSV                                  │
│ 输出: SaeRxUpdateVar 函数代码片段                         │
└─────────────────────────────────────────────────────────┘
    ↓
完整代码：.h 文件 + .c 代码片段
```

---

## 🚀 使用步骤

### Step 1: 生成协议头文件 (.h)

使用 **dbc-to-header** skill 从 CSV 生成协议头文件。

**命令格式：**
```bash
uv run python .github/skills/dbc-to-header/scripts/dbc2header.py csv \
    <CSV文件路径> \
    --baud <波特率> \
    --rx-id <接收帧ID> \
    -o <输出.h文件路径> \
    -p <项目名称>
```

**参数说明：**
- `<CSV文件路径>`：协议 CSV 文件路径
- `--baud`：CAN 波特率（250 或 500）
- `--rx-id`：接收帧 ID（十六进制格式，如 `0x0CFF05EF`，可多次指定）
- `-o`：输出头文件路径（可选，默认为 `<csv名>.h`）
- `-p`：项目名称（可选，默认为 `Motor`）

**示例：**
```bash
uv run python .github/skills/dbc-to-header/scripts/dbc2header.py csv \
    outputs/GTAKE_motor_unified.csv \
    --baud 250 \
    --rx-id 0x0CFF05EF \
    -o outputs/GTAKE_motor_protocol.h \
    -p GTAKE
```

**输出文件内容：**
- 宏定义（接收/发送帧数量、波特率、帧格式、周期）
- 接收消息结构体（如 `TYPE_MOT_RX_APP1`）
- 发送消息结构体（如 `TYPE_MOT_TX1`, `TYPE_MOT_TX2`...）
- 联合体定义（`SAE_DATA`）

---

### Step 2: AI 分析并提取配置 (⚠️ 人工操作)

**此步骤由 AI 大模型人工分析完成，不使用脚本自动化。**

#### 任务说明

AI 需要分析以下内容：
1. **CSV 协议文件**：查看所有接收消息的信号定义
2. **生成的 .h 文件**：确认接收消息的结构体名称（如 `TYPE_MOT_RX_APP1`）
3. **控制器需求**：理解控制器需要哪些输出变量

#### 配置文件格式

生成 `config.json`，包含以下字段：

```json
{
  "msg_id": "0x0CFF05EF",
  "msg_struct": "g_SaeRxMsg[0].Data.MotRx1",
  
  "mapping_analysis": {
    "description": "映射分析说明",
    "rx_message": "接收消息名称",
    "total_signals_in_protocol": 10,
    "signals_used_in_function": 10,
    "signals_missing": 0
  },
  
  "numbers": [
    {"signal_name": "TM_Demand_Torque", "start_bit": 32, "length": 16, "scale": 1, "offset": -5000, "output_var": "RefTempTorq"},
    {"signal_name": "TM_Demand_Speed", "start_bit": 48, "length": 16, "scale": 1, "offset": -15000, "output_var": "RxSpdRefValue"}
  ],
  
  "switches": [
    {"signal_name": "TM_MCU_Enable", "output_field": "RunOrStop", "logic_type": "simple", "params": ""},
    {"signal_name": "TM_Control_Mode", "output_field": "SpdTorqModSel", "logic_type": "cond", "params": "1:1,2:0,3:0,*:0"},
    {"signal_name": "TM_Gear", "output_field": "Direction", "logic_type": "complex", "params": "gear"},
    {"signal_name": "TM_FootBrake", "output_field": "Braking", "logic_type": "or", "params": "TM_HandBrake"}
  ],
  
  "has_gear": true,
  "has_active_discharge": true,
  "active_discharge_signal": "TM_Control_Mode",
  "active_discharge_value": 3,
  
  "missing": [
    {
      "output_var": "RxDrvTorLimValue",
      "searched_signals": ["驱动转矩限制"],
      "found": false,
      "action": "default_zero"
    }
  ]
}
```

#### 配置字段说明

**基本信息：**
- `msg_id`：接收消息 ID
- `msg_struct`：接收消息结构体的访问路径（从 .h 文件的联合体中确定）

**数值信号 (numbers)：**
- `signal_name`：信号名称（从 CSV 提取）
- `start_bit`：起始位（从 CSV 提取）
- `length`：长度（从 CSV 提取）
- `scale`：缩放系数（从 CSV 提取）
- `offset`：偏移量（从 CSV 提取）
- `output_var`：输出变量名（根据控制器需求确定）

**开关量信号 (switches)：**
- `signal_name`：信号名称（从 CSV 提取）
- `output_field`：输出字段名（位域结构体的字段名）
- `logic_type`：逻辑类型（`simple`/`cond`/`complex`/`or`）
- `params`：参数（条件判断的值映射关系）

**逻辑类型说明：**
- `simple`：直接赋值（如 `RunOrStop = TM_MCU_Enable`）
- `cond`：条件判断（如 `if (mode==1) {sel=1;} else {sel=0;}`）
- `complex`：复杂逻辑（如档位处理：N/D/R 档的分支逻辑）
- `or`：或逻辑（如 `Braking = FootBrake OR HandBrake`）

---

### Step 3: 生成接收解析代码 (.c)

使用 **csv-to-source** skill 生成 `SaeRxUpdateVar` 函数代码。

**命令格式：**
```bash
uv run python .github/skills/csv-to-source/script/generate_sae_rx_update_var.py generate \
    <config.json路径> \
    <CSV文件路径> \
    --output <输出.c文件路径>
```

**示例：**
```bash
uv run python .github/skills/csv-to-source/script/generate_sae_rx_update_var.py generate \
    outputs/config.json \
    outputs/GTAKE_motor_unified.csv \
    --output outputs/GTAKE_motor_controller.c
```

**输出文件内容：**
- 缺失信号的默认赋值（如 `RxDrvTorLimValue = 0;`）
- 数值信号的解码（使用 `SignalDecode` 函数）
- 开关量信号的赋值（简单赋值、条件判断、或逻辑）
- 档位处理逻辑（N/D/R 档的分支代码）
- 主动放电控制逻辑
- 速度方向判断（根据转速正负）

---

## ⚠️ 重要说明

### 1. 代码片段性质

**生成的 .c 文件是代码片段，不是完整的独立源文件：**
- ✅ 包含 `SaeRxUpdateVar` 函数的核心逻辑代码
- ✅ 可以直接插入到现有的控制器源文件中
- ❌ 不包含文件头、函数签名、全局变量声明
- ❌ 不是可以独立编译的完整文件

**使用方式：**
将生成的代码片段复制到控制器的源文件中，替换或补充 `SaeRxUpdateVar` 函数的实现部分。

### 2. 无需语法检查

生成的代码片段是模板化输出，**不需要进行语法检查或编译验证：**
- 代码片段遵循固定的模板格式
- 由嵌入式开发人员根据实际项目进行集成和调整
- AI 工具只需确保配置正确、逻辑清晰即可

### 3. Step 2 不使用脚本

**配置提取步骤（Step 2）必须由 AI 大模型人工完成：**
- ✅ AI 需要理解协议语义（如"转矩"、"转速"、"档位"等）
- ✅ AI 需要根据控制器需求建立映射关系
- ✅ AI 需要判断信号的处理逻辑类型（simple/cond/complex/or）
- ❌ 不要使用脚本自动化此步骤，因为需要语义理解和决策

---

## 📊 完整示例

### 输入文件

**outputs/GTAKE_motor_unified.csv**
```csv
消息ID,消息名称,消息长度,周期时间(ms),发送者,消息备注(JSON),信号名称,起始位,长度(bit),字节序,有符号,初值,缩放系数,偏移,最小值,最大值,单位,接收者,备注(JSON)
0x0CFF05EF,TM_HCU_Command,8,10,HCU,,TM_MCU_Enable,0,1,little_endian,否,,1,0,0,1,,TM_MCU,"{""0"": ""disable"", ""1"": ""enable""}"
0x0CFF05EF,TM_HCU_Command,8,10,HCU,,TM_Demand_Torque,32,16,little_endian,否,,1,-5000,-5000,5000,Nm,TM_MCU,"{""description"": ""转矩指令""}"
...
```

### Step 1: 生成头文件

```bash
uv run python .github/skills/dbc-to-header/scripts/dbc2header.py csv \
    outputs/GTAKE_motor_unified.csv \
    --baud 250 \
    --rx-id 0x0CFF05EF \
    -o outputs/GTAKE_motor_protocol.h \
    -p GTAKE
```

**输出：outputs/GTAKE_motor_protocol.h**
```c
#define SAE_MAX_RX_NUM 1
#define SAE_MAX_TX_NUM 3
#define BAUD250 1

typedef struct __MOT_RX_APP1 {
    unsigned TM_MCU_Enable : 1;
    unsigned TM_Demand_Torque_L : 8;
    unsigned TM_Demand_Torque_H : 8;
    // ...
} TYPE_MOT_RX_APP1;

typedef union __SAE_DATA {
    TYPE_MOT_RX_APP1 MotRx1;  // TM_HCU_Command
    // ...
} SAE_DATA;
```

### Step 2: AI 提取配置

AI 分析 CSV 和 .h 文件后，创建 **outputs/config.json**：

```json
{
  "msg_id": "0x0CFF05EF",
  "msg_struct": "g_SaeRxMsg[0].Data.MotRx1",
  "numbers": [
    {"signal_name": "TM_Demand_Torque", "start_bit": 32, "length": 16, "scale": 1, "offset": -5000, "output_var": "RefTempTorq"}
  ],
  "switches": [
    {"signal_name": "TM_MCU_Enable", "output_field": "RunOrStop", "logic_type": "simple", "params": ""}
  ],
  "has_gear": true,
  "missing": []
}
```

### Step 3: 生成 C 代码

```bash
uv run python .github/skills/csv-to-source/script/generate_sae_rx_update_var.py generate \
    outputs/config.json \
    outputs/GTAKE_motor_unified.csv \
    --output outputs/GTAKE_motor_controller.c
```

**输出：outputs/GTAKE_motor_controller.c**（代码片段）
```c
// RefTempTorq(单位NM)
// TM_Demand_Torque 起始位:32 长度:16 系数:1 偏移量:-5000 单位:Nm
raw = ((Uint16)g_SaeRxMsg[0].Data.MotRx1.TM_Demand_Torque_L & 0x00FF) | 
      ((Uint16)g_SaeRxMsg[0].Data.MotRx1.TM_Demand_Torque_H << 8);
RefTempTorq = SignalDecode(raw, IN_RATIO(1), OUT_RATIO(1), -5000L);

// TM_MCU_Enable 起始位:0 长度:1 系数:1 偏移量:0
VehicleCmdCanTemp.B.RunOrStop = g_SaeRxMsg[0].Data.MotRx1.TM_MCU_Enable;
```

---

## 🎓 AI 使用指南

### 何时使用此 skill

当用户请求以下内容时，使用本 skill：
- "从 CSV 生成控制器代码"
- "生成 CAN 协议的 .c 和 .h 文件"
- "需要完整的控制器接收解析代码"
- "生成 SaeRxUpdateVar 函数"

### AI 操作流程

1. **确认输入参数**
   - CSV 文件路径
   - 波特率（250 或 500）
   - 接收帧 ID（从需求文档或 CSV 中提取）
   - 项目名称（可选）

2. **执行 Step 1**
   - 运行 dbc-to-header 命令生成 .h 文件
   - 确认生成成功并查看输出

3. **执行 Step 2（关键步骤）**
   - 读取 CSV 文件内容
   - 读取生成的 .h 文件内容
   - 分析接收消息的信号
   - 确定每个信号对应的输出变量和处理逻辑
   - 创建 config.json 文件
   - ⚠️ 此步骤完全由 AI 分析和决策，不调用任何脚本

4. **执行 Step 3**
   - 运行 csv-to-source 命令生成 .c 代码片段
   - 确认生成成功

5. **汇报结果**
   - 列出生成的文件路径
   - 说明代码片段的使用方式
   - 提醒用户代码需要集成到项目中

### 常见问题处理

**Q: 如何确定接收帧 ID？**
A: 查看 CSV 中"发送者"列，发送者为 HCU/VCU 的消息通常是控制器的接收消息。

**Q: 如何确定 msg_struct 的值？**
A: 查看生成的 .h 文件中的联合体定义，接收消息结构体的字段名（如 `MotRx1`）组合数组访问（如 `g_SaeRxMsg[0].Data.MotRx1`）。

**Q: 如何判断信号的逻辑类型？**
A: 
- `simple`：单个位，直接赋值
- `cond`：多个值映射到不同输出（如控制模式 1=速度，2=转矩）
- `complex`：档位信号（N/D/R 档需要多个字段赋值）
- `or`：多个信号做或运算（如脚刹 OR 手刹）

---

## 📁 文件组织建议

```
outputs/
├── <项目名>_unified.csv          # 输入：协议 CSV 文件
├── <项目名>_protocol.h           # 输出：协议头文件（Step 1）
├── config.json                    # 中间：配置文件（Step 2）
└── <项目名>_controller.c         # 输出：接收解析代码片段（Step 3）
```

---

## ✅ 成功标准

完成以下输出即为成功：
1. ✅ `.h 文件`：包含完整的结构体定义和宏定义
2. ✅ `config.json`：包含正确的信号映射配置
3. ✅ `.c 文件`：包含 SaeRxUpdateVar 函数的实现代码片段

无需进行编译测试或语法检查，生成的代码片段供嵌入式工程师集成使用。

---

## 🔗 依赖 Skills

- **dbc-to-header**: 生成协议头文件
- **csv-to-source**: 生成接收解析代码

确保这两个 skills 在工作区可用。
