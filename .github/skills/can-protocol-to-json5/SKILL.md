---
name: can-protocol-to-json5
description: >
  将汽车 CAN 通讯协议文档（PDF、Word、图片）中的报文和信号定义提取并转换为
  单个标准化 JSON5 格式。必须在以下场景中使用本 skill：用户上传了通讯协议 PDF/文档并要求
  提取某个 ECU 节点（如油泵DC/AC、气泵ACM、MCU、VCU）的报文信号；
  用户提到"通讯协议转换"、"报文提取"、"信号提取"、"协议文档转json5"、"DBC提取"、
  "CAN报文定义"、"SAE J1939协议"、"从协议PDF提取信号"等关键词时。
  即使用户只说"提取报文"或"转换协议"也应触发本 skill。
---

# CAN 通讯协议文档 → JSON5 转换 Skill

## 文件结构

```
can-protocol-to-json5/
├── SKILL.md                          ← 主流程（本文件）
└── references/
    ├── rules.md                      ← 完整规则手册（信号解析、陷阱、MIN/MAX换算）
    ├── gen_script_template.py        ← Python 生成脚本模板（可直接运行）
    └── EHPS_example.json5            ← 油泵DC/AC 完整转换示例（含故障位展开）
```

**使用时机**：先读本文件快速掌握流程；遇到具体规则疑问时读 `references/rules.md`；
需要生成脚本时用 `references/gen_script_template.py`。

---

## 快速流程（6 步）

### Step 1  确认转换范围

从对话或文档中确认：
- **目标节点**（如 `EHPS`/油泵DC/AC）及其对端（通常 `VCU`）
- **目标章节**（如"7.2 油泵DC/AC报文"）
- **字节序**：默认 Intel，Motorola 会在文档中特别注明（如绝缘检测仪 ICU）

### Step 2  读取节点地址

在文档"节点地址分配"表中查找：
- 目标节点的 **SourceAddress**（十六进制）
- 用于验证 CAN ID，公式：`CAN_ID = (Priority<<26) | (PGN<<8) | SourceAddress`

常用节点速查（中通客车协议 BZYFG-000102）：

| 节点 | 缩写 | 地址 |   | 节点 | 缩写 | 地址 |
|------|------|------|---|------|------|------|
| 整车控制器 | VCU | 0xEF | | 高压转低压 | DC/DC | 0x9A |
| 电机控制器 | MCU | 0x08 | | 油泵DC/AC | EHPS | 0x9B |
| 电池管理 | BMS | 0xF3 | | 气泵DC/AC | ACM  | 0x9D |
| 绝缘检测仪 | ICU | 0xA4 | | 高压控制板 | HVB  | 0x9F |

### Step 3  逐条解析报文

对每条报文提取：`ID`、`DLC`、`TransmissionRate`、`TXNODE`、`RXNODE`，
然后逐行读取信号表（StartBit / LengthBit / Signal / Scale / Offset / Unit / Min / Max）。

**关键判断（详见 `references/rules.md`）**：
- 保留位 → **直接省略**（含 Reserved / 保留 / 预留 / 备用）
- 故障代码字节有 Bit 明细表 → **逐位展开**为独立 1bit 信号
- MIN/MAX → 填**总线原始整数值**，非物理值
- 故障代码字节有"此位不能查询" → 该 bit **省略**

### Step 4  确定 MSGNAME 和方向

以 **NODE2（目标 ECU）** 为视角命名：
- NODE2 **接收**（对端发出）→ `Rx{N}_0x{ID}`
- NODE2 **发送** → `Tx{N}_0x{ID}`
- N 从 0 开始，按文档顺序编号

### Step 5  生成 JSON5

调用 `references/gen_script_template.py` 的 `sig_line()` 函数格式化每个信号，
输出符合以下结构的 JSON5：

```json5
{
    // 来源：协议文档名称及版本
    // 协议：SAE J1939，CAN 2.0B，29位ID，250Kbs，Intel字节序
    // 节点地址：NODE1=0xXX  NODE2=0xXX

    NODE1: "VCU",
    NODE2: "EHPS",
    MSGS: [
// +------------------------------------------------------------+

    // [100ms] 报文功能描述
    {ID: 0x1801A79B, MSGNAME: "Tx1_0x1801A79B", DLC: 8, TXNODE:"EHPS", RXNODE:"VCU", SIGS:[
        {SIG: "EHPS_InputVolt            ",  SBIT: 0,  LEN: 16, FACTOR: 1,   OFFSET: 0,   MIN: 0, MAX: 1000, UINT:"V",  COMMENT: "Input voltage 输入电压"},
        {SIG: "EHPS_FaultUnderVolt       ",  SBIT: 56, LEN: 1,  FACTOR: 1,   OFFSET: 0,   MIN: 0, MAX: 1,    UINT:"",  COMMENT: "输入欠压故障 0=正常 1=故障"},
    ]},
// +------------------------------------------------------------+
    ]
}
```

### Step 6  输出与交付

1. 写入 `/mnt/user-data/outputs/{NODE}_{功能}_CAN.json5`
2. 调用 `present_files` 提供下载
3. 附简要说明：报文数、信号数、特殊处理（保留位省略数量、故障位展开情况）

---

## 最常见的 5 个陷阱（快速参考）

| # | 陷阱 | 正确做法 |
|---|------|---------|
| 1 | MIN/MAX 填了物理值 | 换算为总线原始整数：`bus = (phys - offset) / factor` |
| 2 | 故障代码合并为 1 个 8bit 信号 | 有 Bit 明细时逐位展开，每位 LEN=1 |
| 3 | 保留位写进 JSON5 | 直接省略，在注释中说明跳过了多少位 |
| 4 | Motorola 格式当 Intel 处理 | 文档有特别注明时在报文注释中标 `⚠️ Motorola` |
| 5 | 多字节信号拆成高低字节两条 | 合并为一条，SBIT 取低字节位置，LEN 相加 |

> 完整规则、换算示例、枚举值写法 → 见 `references/rules.md`
>
> 完整转换示例（含故障位展开）→ 见 `references/EHPS_example.json5`
