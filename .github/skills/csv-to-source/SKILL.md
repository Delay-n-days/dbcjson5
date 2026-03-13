---
name: csv-to-source
description: >
    注意: 这个skill是control-code-generator 的 子功能,请优先阅读control-code-generator skill
    
    从 CAN 协议 CSV 自动生成 C 语言源代码，包含信号解析函数、数据结构定义和注释。支持数值信号的缩放/偏移处理，开关量信号的条件判断，以及复杂逻辑的代码生成。
    适用场景：用户需要从 CAN 协议 CSV 生成 C 语言源代码；或用户提到 "CSV转C代码"、"协议CSV生成C源文件"、"CAN信号解析函数"、"数据结构定义"、"数值信号处理"、"开关量条件判断"、"复杂逻辑代码生成" 等关键词时，必须使用本 skill。
    本 skill 内置 generate_sae_rx_update_var.py 脚本，无需用户额外上传转换工具。
---



# SAE协议SaeRxUpdateVar函数生成 Skill

## 🎯 核心功能

从**CAN协议CSV**自动生成C函数 `SaeRxUpdateVar`（接收数据解析函数）。

---

## ⚠️ 最关键的一步：DBC信号映射

**这是整个工作流的核心，也是最容易出错的地方。**

### 问题场景

函数需要输出这些变量：
```c
RxTorRefValue              // 目标转矩(Nm)
RxSpdRefValue              // 目标转速(rpm)
RxFwdSpdLimValue           // 正转速度限制(rpm)
RxRevSpdLimValue           // 反转速度限制(rpm)
RxDrvTorLimValue           // 驱动转矩限制(Nm)  ← 协议中有吗？
RxBrkTorLimValue           // 制动转矩限制(Nm)  ← 协议中有吗？
VehicleCmdCanTemp          // 位域结构体
```

**你必须找出：每个输出变量 ↔ DBC信号名称的映射关系**

### 映射方式

从协议CSV中找信号，建立映射表：

| 输出变量 | 对应DBC信号 | 信号位置 | 缺失处理 |
|---------|----------|--------|--------|
| RxTorRefValue | TM_Demand_Torque | 32位, 16长 | ✅ 找到 |
| RxSpdRefValue | TM_Demand_Speed | 48位, 16长 | ✅ 找到 |
| RxFwdSpdLimValue | TM_Demand_Limit_High | 8位, 12长 | ✅ 找到 |
| RxRevSpdLimValue | TM_Demand_Limit_Low | 20位, 12长 | ✅ 找到 |
| RxDrvTorLimValue | ❌ 不存在 | - | 默认赋0 |
| RxBrkTorLimValue | ❌ 不存在 | - | 默认赋0 |
| VehicleCmdCanTemp.B.RunOrStop | TM_MCU_Enable | 0位, 1长 | ✅ 找到 |
| VehicleCmdCanTemp.B.FaultReset | TM_Fault_Reset | 1位, 1长 | ✅ 找到 |
| ... | ... | ... | ... |

---

## 📖 AI提取的详细步骤

### Step 1: 分析协议CSV的接收消息

首先，**识别接收消息**：
- 消息ID (如 0x0CFF05EF)
- 消息名 (如 TM_HCU_Command)
- 对应的结构体类型 (如 TYPE_MOT_RX_APP1)
- 结构体访问路径 (如 g_SaeRxMsg[0].Data.MotRx1)

**AI提示：** 查看协议CSV，筛选"发送者"为HCU或VCU的消息，这通常是接收消息。

---

### Step 2: 建立输出变量与DBC信号的映射表

**这是最关键的一步！**

AI需要逐个检查函数要输出的每个变量，**在协议CSV中查找对应的信号**。

#### 纯数值输出变量（需要SignalDecode）

```
RxTorRefValue      → 在CSV中查找 "转矩" 相关信号
                     ✓ 找到: TM_Demand_Torque (32位, 16长, 缩放1, 偏移-5000)

RxSpdRefValue      → 在CSV中查找 "转速" 相关信号
                     ✓ 找到: TM_Demand_Speed (48位, 16长, 缩放1, 偏移-15000)

RxFwdSpdLimValue   → 在CSV中查找 "正转速度限制" 或 "转速上限"
                     ✓ 找到: TM_Demand_Limit_High (8位, 12长, 缩放4, 偏移0)

RxRevSpdLimValue   → 在CSV中查找 "反转速度限制" 或 "转速下限"
                     ✓ 找到: TM_Demand_Limit_Low (20位, 12长, 缩放4, 偏移0)

RxDrvTorLimValue   → 在CSV中查找 "驱动转矩限制" 信号
                     ✗ 未找到 → 默认赋0

RxBrkTorLimValue   → 在CSV中查找 "制动转矩限制" 信号
                     ✗ 未找到 → 默认赋0
```

#### 位域结构体的输出字段（开关量/枚举）

```
VehicleCmdCanTemp.B.RunOrStop      → 查找 "MCU使能" / "运行指令"
                                     ✓ TM_MCU_Enable (0位, 1长)

VehicleCmdCanTemp.B.FaultReset    → 查找 "故障复位"
                                     ✓ TM_Fault_Reset (1位, 1长)

VehicleCmdCanTemp.B.SpdTorqModSel → 查找 "控制模式" / "速度转矩选择"
                                     ✓ TM_Control_Mode (2位, 2长)
                                        值1=速度控制 → 输出1
                                        值2=转矩控制 → 输出0

VehicleCmdCanTemp.B.Direction     → 查找 "档位" / "方向"
VehicleCmdCanTemp.B.ReDirection   → 同上
VehicleCmdCanTemp.B.NeutralPosition → 同上
                                     ✓ TM_Gear (4位, 2长)
                                        值1=D档, 值2=R档, 值0=N档

VehicleCmdCanTemp.B.Braking       → 查找 "脚刹" 或 "制动"
                                     ✓ TM_FootBrake (6位, 1长)
                                     ✓ TM_HandBrake (7位, 1长)
                                        逻辑: Braking = FootBrake OR HandBrake

VehicleCmdCanTemp.B.FwdOrRev      → 程序自动推导（根据RxSpdRefValue正负）
                                     无需CSV信号

VehicleCmdCanTemp.B.mainctrl      → 查找 "主动放电" / "能量回收"
                                     ✓ TM_Control_Mode (2位, 2长)
                                        值3=主动放电 → 输出1
```

---

### Step 3: 识别信号的处理类型

对找到的每个信号，**判断其处理逻辑**：

#### A. 纯数值信号（需要SignalDecode）

特征：
- 长度 > 8位（跨字节）
- 有缩放系数（不是1）或有偏移值（不是0）

例子：
```
TM_Demand_Torque
  - 长度: 16位 > 8 ✓
  - 缩放: 1
  - 偏移: -5000 ✓
  → 需要SignalDecode
  → raw需要_L和_H拼接

TM_Demand_Limit_High
  - 长度: 12位 > 8 ✓
  - 缩放: 4 (不是1) ✓
  - 偏移: 0
  → 需要SignalDecode
  → raw需要_L和_H拼接
```

#### B. 开关量/枚举信号（直接赋值）

特征：
- 长度 ≤ 8位（单字节内）
- 缩放 = 1, 偏移 = 0

处理逻辑：
- **simple**: 直接赋值
  ```
  TM_MCU_Enable (0位, 1长) → RunOrStop
  VehicleCmdCanTemp.B.RunOrStop = g_SaeRxMsg[0].Data.MotRx1.TM_MCU_Enable;
  ```

- **cond**: 条件判断（有多个值对应不同输出）
  ```
  TM_Control_Mode (2位, 2长)
    值0 → 无效(默认0)
    值1 → 速度控制(输出1)
    值2 → 转矩控制(输出0)
    值3 → 主动放电(输出0)
  → 参数: "1:1,2:0,3:0,*:0"
  ```

- **complex**: 复杂转换（档位逻辑特有）
  ```
  TM_Gear (4位, 2长)
    值0 → N档: Direction=0, ReDirection=0, NeutralPosition=1, RefTempTorq=0
    值1 → D档: Direction=1, ReDirection=0, NeutralPosition=0
    值2 → R档: Direction=0, ReDirection=1, NeutralPosition=0, RefTempTorq取反
  → 逻辑类型: "complex"
  ```

- **or**: 或逻辑（多个信号做布尔运算）
  ```
  TM_FootBrake (6位, 1长) OR TM_HandBrake (7位, 1长) → Braking
  → 参数: "TM_HandBrake"
  → 生成: if((signal1 == 1) || (signal2 == 1)) Braking = 1;
  ```

---

### Step 4: 生成Config JSON

根据上述分析，生成最终的JSON配置。

**必须包含的信息：**

```json
{
  "msg_id": "0x0CFF05EF",
  "msg_struct": "g_SaeRxMsg[0].Data.MotRx1",
  
  "mapping_analysis": {
    "description": "映射分析过程（注释，便于人类review）",
    "rx_message": "TM_HCU_Command",
    "total_signals_in_protocol": 10,
    "signals_used_in_function": 8,
    "signals_missing": 2
  },
  
  "numbers": [
    ["TM_Demand_Torque", 32, 16, 1, -5000, "RefTempTorq"],
    ["TM_Demand_Speed", 48, 16, 1, -15000, "RxSpdRefValue"],
    ["TM_Demand_Limit_High", 8, 12, 4, 0, "RxFwdSpdLimValue"],
    ["TM_Demand_Limit_Low", 20, 12, 4, 0, "RxRevSpdLimValue"]
  ],
  
  "switches": [
    ["TM_MCU_Enable", "RunOrStop", "simple", ""],
    ["TM_Fault_Reset", "FaultReset", "simple", ""],
    ["TM_Control_Mode", "SpdTorqModSel", "cond", "1:1,2:0,3:0,*:0"],
    ["TM_Gear", "Gear", "complex", ""],
    ["TM_FootBrake", "Braking", "or", "TM_HandBrake"]
  ],
  
  "has_gear": true,
  
  "missing": [
    {
      "output_var": "RxDrvTorLimValue",
      "searched_signals": ["驱动转矩限制", "Drive Torque Limit"],
      "found": false,
      "action": "default_zero"
    },
    {
      "output_var": "RxBrkTorLimValue",
      "searched_signals": ["制动转矩限制", "Brake Torque Limit"],
      "found": false,
      "action": "default_zero"
    }
  ]
}
```

---

## 🤖 完整AI Prompt（严格要求映射）

```
【任务】根据CAN协议CSV，为SaeRxUpdateVar函数生成config.json

【第一步】分析接收消息
请找出协议中的接收消息（发送者为HCU或VCU的消息）：
- 消息ID
- 消息名称
- 对应的结构体类型和访问路径

【第二步】建立映射表（最关键）
函数需要以下输出变量，请在协议CSV中逐个查找对应的DBC信号：

纯数值变量：
- RxTorRefValue → 查找关键词: "转矩", "Torque", "Demand"
- RxSpdRefValue → 查找关键词: "转速", "Speed", "rpm"
- RxFwdSpdLimValue → 查找关键词: "正转速度限制", "Speed Limit High"
- RxRevSpdLimValue → 查找关键词: "反转速度限制", "Speed Limit Low"
- RxDrvTorLimValue → 查找关键词: "驱动转矩限制", "Drive Torque Limit"
- RxBrkTorLimValue → 查找关键词: "制动转矩限制", "Brake Torque Limit"

位域变量（开关量/枚举）：
- VehicleCmdCanTemp.B.RunOrStop → 查找: "使能", "Enable", "Run"
- VehicleCmdCanTemp.B.FaultReset → 查找: "故障复位", "Fault Reset"
- VehicleCmdCanTemp.B.SpdTorqModSel → 查找: "控制模式", "Control Mode"
- VehicleCmdCanTemp.B.Direction/ReDirection/NeutralPosition → 查找: "档位", "Gear"
- VehicleCmdCanTemp.B.Braking → 查找: "脚刹", "手刹", "制动", "Brake"
- VehicleCmdCanTemp.B.mainctrl → 查找: "主动放电", "能量回收", "Active Discharge"

对每个变量，请输出：
  ✓ 如果找到: [信号名, 起始位, 长度, 缩放, 偏移]
  ✗ 如果未找到: [变量名, 搜索关键词, 不存在，建议默认赋0]

【第三步】判断处理逻辑
对每个找到的信号，判断其处理类型：
- 长度>8位 或 有缩放/偏移 → numeric (需要SignalDecode)
- 长度≤8位 且 缩放=1,偏移=0 → switch
  - 单值赋值 → simple
  - 多值条件判断 → cond (列出所有值的映射)
  - 档位特殊处理 → complex (说明N/D/R档的逻辑)
  - 多信号或运算 → or (指定另一信号)

【第四步】输出最终JSON

```json
{
  "msg_id": "...",
  "msg_struct": "...",
  "numbers": [[信号名, 起始位, 长度, 缩放, 偏移, 输出变量], ...],
  "switches": [[信号名, 输出字段, 逻辑类型, 参数], ...],
  "has_gear": true/false,
  "missing": [
    {
      "output_var": "RxDrvTorLimValue",
      "searched_signals": ["驱动转矩限制", "..."],
      "found": false,
      "action": "default_zero"
    },
    ...
  ]
}
```

【关键要求】
1. ✅ 必须显式列出所有搜索过程（找到的 + 未找到的）
2. ✅ 必须说明每个信号的处理类型（numeric/simple/cond/complex/or）
3. ✅ 必须清楚地说明cond的值映射和complex的逻辑分支
4. ✅ 协议中没有的变量必须在missing列表中，不能忽略
5. ✅ 只输出最终JSON，不需要其他说明

【输出】
```json
{
  ...
}
```
```

---

## 📊 Config JSON 完整数据结构

```python
from dataclasses import dataclass
from typing import List

@dataclass
class NumericSignal:
    """纯数值信号（需要SignalDecode）"""
    signal_name: str      # 信号名 (来自协议CSV)
    start_bit: int        # 起始位
    length: int           # 长度(bit)
    scale: int            # 缩放系数
    offset: int           # 偏移值
    output_var: str       # 输出变量名 (来自函数签名)

@dataclass
class SwitchSignal:
    """开关量/枚举信号"""
    signal_name: str      # 信号名 (来自协议CSV)
    output_field: str     # 输出字段 (去掉VehicleCmdCanTemp.B.)
    logic_type: str       # simple/cond/complex/or
    params: str           # 参数 (cond时:"1:1,2:0,*:0"; or时:"TM_HandBrake")

@dataclass
class MissingSignal:
    """缺失信号（协议中没有）"""
    output_var: str           # 输出变量名
    searched_signals: List[str] # 搜索过的关键词
    found: bool               # 是否找到
    action: str               # default_zero / manual_configure

@dataclass
class MappingAnalysis:
    """映射分析信息（可选但推荐）"""
    description: str          # 人类可读的分析说明
    rx_message: str           # 接收消息名
    total_signals_in_protocol: int  # 协议中总信号数
    signals_used: int         # 函数使用的信号数
    signals_missing: int      # 缺失的信号数

@dataclass
class Config:
    """根配置"""
    msg_id: str                           # 消息ID
    msg_struct: str                       # 结构体路径
    numbers: List[NumericSignal]          # 纯数值信号
    switches: List[SwitchSignal]          # 开关量信号
    has_gear: bool                        # 是否有档位
    missing: List[MissingSignal]          # 缺失信号列表
    mapping_analysis: MappingAnalysis = None  # 可选的分析说明
```

---

## ⚙️ 重要技术说明

### 1. IN_RATIO 固定为 1，OUT_RATIO 使用信号缩放系数

**所有生成的代码中，`IN_RATIO` 固定为 1，`OUT_RATIO` 使用信号的 `scale` 字段。**

```c
// 生成的代码示例
RefTempTorq = SignalDecode(raw, IN_RATIO(1), OUT_RATIO(1), -5000L);      // scale=1
RxSpdRefValue = SignalDecode(raw, IN_RATIO(1), OUT_RATIO(1), -15000L);   // scale=1
RxFwdSpdLimValue = SignalDecode(raw, IN_RATIO(1), OUT_RATIO(1), 0L);     // scale=1
```

**原因：**
- `IN_RATIO` 固定为 1，不使用 CSV 中的缩放系数
- `OUT_RATIO` 使用信号的 `scale` 字段（大多数信号的 scale 为 1）
- 控制器内部统一使用实际物理单位（Nm、rpm等）
- `SignalDecode` 函数通过 `offset` 参数处理偏移量

### 2. RefTempTorq 局部变量声明

**生成的代码会自动声明局部变量 `RefTempTorq`：**

```c
// 局部变量声明
long RefTempTorq = 0;  // 扭矩给定（临时变量）

// RefTempTorq(单位NM)
// DemandTorque	起始位:32	长度:16	系数:1.0	偏移量:-5000.0	单位:Nm
raw = ((Uint16)g_SaeRxMsg[0].Data.MotRx1.DemandTorque_L & 0x00FF) | 
      ((Uint16)g_SaeRxMsg[0].Data.MotRx1.DemandTorque_H << 8);
RefTempTorq = SignalDecode(raw, IN_RATIO(1), OUT_RATIO(1), -5000L);

// ...其他处理...

RxTorRefValue = RefTempTorq;  // 最终赋值给全局变量
```

**说明：**
- `RefTempTorq` 作为临时变量存储解码后的转矩值
- 在档位处理、主动放电等逻辑中可能被修改（如清零）
- 最后赋值给全局变量 `RxTorRefValue`

### 3. 缺失信号的特殊处理

对于包含多个变量名的缺失信号（如档位相关），脚本会自动拆分处理：

**配置示例：**
```json
{
  "output_var": "VehicleCmdCanTemp.B.Direction/ReDirection/NeutralPosition",
  "searched_signals": ["档位", "Gear"],
  "found": false,
  "action": "default_zero"
}
```

**生成代码：**
```c
//VehicleCmdCanTemp.B.Direction/ReDirection/NeutralPosition(单位NM)
lngTemp1 = 0;  // DBC 未提及，默认赋值为0
VehicleCmdCanTemp.B.Direction = lngTemp1;
VehicleCmdCanTemp.B.ReDirection = lngTemp1;
VehicleCmdCanTemp.B.NeutralPosition = lngTemp1;
```

**注意：** 使用斜杠 `/` 分隔多个变量名，脚本会自动为每个变量生成独立的赋值语句。

### 4. 档位处理的默认代码

**无论是否有档位信号，都会生成档位处理代码块：**

- **has_gear = true**：`#if 1` + 实际的档位信号处理代码
- **has_gear = false**：`#if 0` + 默认的档位处理模板代码

**默认模板代码示例（has_gear = false 时）：**
```c
#if 0 //无挡位软件更改为:#if 0

//手刹和脚刹信号有效均将VehicleCmdCanTemp.B.Braking赋为1
// TM_FootBrake	起始位:6	长度:1	系数:1	偏移量:0	0:No FootBrake;1:FootBrake
if((g_SaeRxMsg[0].Data.MotRx1.TM_FootBrake == 1)||(g_SaeRxMsg[0].Data.MotRx1.TM_HandBrake == 1))
{
	VehicleCmdCanTemp.B.Braking = 1;
}
else
{
	VehicleCmdCanTemp.B.Braking = 0;	
}
//挡位信号赋值
// TM_Gear	起始位:4	长度:2	系数:1	偏移量:0	0:Neutral;1:Drive;2:Reverse
if(g_SaeRxMsg[0].Data.MotRx1.TM_Gear == 1)
{//D挡
	VehicleCmdCanTemp.B.Direction=1;
	VehicleCmdCanTemp.B.ReDirection = 0;
	VehicleCmdCanTemp.B.NeutralPosition = 0;
}
else if(g_SaeRxMsg[0].Data.MotRx1.TM_Gear == 2)
{//R挡
	VehicleCmdCanTemp.B.Direction=0;
	VehicleCmdCanTemp.B.ReDirection = 1;
	VehicleCmdCanTemp.B.NeutralPosition = 0;
	//协议规定,R挡电动发负扭矩,此处保证送入底层电动为正扭矩
	RefTempTorq = 0 - RefTempTorq;
}
else
{//N挡
	VehicleCmdCanTemp.B.Direction=0;
	VehicleCmdCanTemp.B.ReDirection = 0;	  
	VehicleCmdCanTemp.B.NeutralPosition = 1;
	RefTempTorq = 0;//空挡扭矩清零
}

#endif
```

**说明：**
- 默认模板提供完整的档位处理逻辑，即使协议中没有档位信号
- 工程师可以根据实际需要修改 `#if 0` 为 `#if 1` 来启用
- 保证代码结构的一致性和可维护性

---

## 使用步骤

### 1. 准备协议CSV

确保包含所有接收消息的信号定义。

### 2. 运行AI Prompt

将上面的"完整AI Prompt"复制到Claude，粘贴你的协议CSV。

### 3. 验证映射表

**重点检查：**
- ✅ missing列表中的每个变量是否真的搜索过了？
- ✅ cond逻辑的值映射是否完整？
- ✅ complex的档位逻辑是否正确描述？
- ✅ or信号是否标识正确？

### 4. 运行脚本

```bash
python generate_sae_rx_update_var.py --config config.json --output SaeRxUpdateVar.c
```

---

## 检查清单

生成config.json后，务必验证：

- [ ] msg_id 和 msg_struct 正确
- [ ] numbers 数组中的每个信号在协议CSV中都能找到
- [ ] switches 数组中的每个信号在协议CSV中都能找到
- [ ] cond 类型的参数列出了所有可能的值及其映射
- [ ] complex 类型的参数清楚描述了N/D/R档的处理逻辑
- [ ] or 类型的参数指向了正确的另一信号
- [ ] missing 数组列出了所有协议中不存在的变量
- [ ] has_gear 与是否有TM_Gear信号一致
- [ ] 映射分析（可选）提供了清晰的搜索过程说明