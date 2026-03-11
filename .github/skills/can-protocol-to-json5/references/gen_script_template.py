"""
CAN 通讯协议 PDF → JSON5 生成脚本模板
======================================
使用方法：
  1. 修改顶部配置变量（OUTPUT_PATH / NODE1 / NODE2 / SOURCE_DOC）
  2. 在 msgs 列表中按协议文档填写每条报文和信号
  3. 运行：python3 gen_script_template.py
  4. 检查输出文件，确认信号数量和内容

设计原则（与 SKILL.md 保持一致）：
  - 保留位（Reserved/保留/预留）全部省略
  - 故障代码字节：有 Bit 明细时逐位展开为独立 1bit 信号
  - "此位不能查询"的 Bit → 省略
  - MIN/MAX 填总线原始整数值（非物理值）
  - 信号名 ≤26 字符，补空格对齐
"""

# ─── 配置区（每次使用时修改这里） ───────────────────────────────────────────
OUTPUT_PATH = "/mnt/user-data/outputs/EHPS_OilPump_CAN.json5"
NODE1       = "VCU"
NODE2       = "EHPS"
SOURCE_DOC  = "中通客车多合一集成电机控制器通讯协议 BZYFG-000102 V1.0 第7.2节"
# ────────────────────────────────────────────────────────────────────────────

SEP = '// +' + '-' * 110 + '+'


# ─── 工具函数 ─────────────────────────────────────────────────────────────────

def fmt_id(val: int) -> str:
    """整数 CAN ID → '0x1801A79B' 格式"""
    return f'0x{val:08X}'


def sig(name: str, sbit: int, length: int,
        factor, offset, min_v, max_v,
        unit: str, comment: str) -> str:
    """
    格式化单条信号为 JSON5 文本行。

    参数：
        name    - 信号名，会自动补空格至26字符
        sbit    - 起始位（Intel格式为LSB位编号）
        length  - 位长度
        factor  - 精度（整数传int，小数传float，如 0.1）
        offset  - 偏移量（可为负整数，如 -40）
        min_v   - 总线原始最小值（整数）
        max_v   - 总线原始最大值（整数）
        unit    - 单位，无单位传 ""
        comment - 信号描述，包含中英文和枚举含义

    MIN/MAX 换算速查：
        bus_val = (phys_val - offset) / factor
        温度 -40~210℃, factor=1, offset=-40  → MIN=0, MAX=250
        电流 0~100A,    factor=0.1, offset=0  → MIN=0, MAX=1000
        转速 ±15000rpm, factor=1, offset=-15000 → MIN=0, MAX=30000
    """
    name_pad  = name.ljust(26)
    factor_s  = str(factor)
    offset_s  = str(offset)
    return (
        f'        {{SIG: "{name_pad}",\t'
        f'SBIT: {sbit},\tLEN: {length},\t'
        f'FACTOR: {factor_s},  \tOFFSET: {offset_s},  \t'
        f'MIN: {min_v},  \tMAX: {max_v},   \t'
        f'UINT:"{unit}",  \tCOMMENT: "{comment}"}},')


# ─── 报文定义（按协议文档章节逐条填写） ─────────────────────────────────────
#
# 每条报文格式：
# {
#   'id'  : int,  完整 CAN ID（29位）
#   'name': str,  MSGNAME，格式 Rx{N}/Tx{N}_0x{ID}
#   'dlc' : int,  帧长度（字节）
#   'tx'  : str,  发送节点名
#   'rx'  : str,  接收节点名
#   'rate': str,  发送周期
#   'desc': str,  报文功能描述
#   'sigs': list, 由 sig() 生成的信号行列表
# }

msgs = []

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Rx0  VCU→EHPS  辅驱开关机控制  ID=0x0C0A88EF  100ms
# 说明：油泵/气泵/DCDC 共用此帧，0xAA=开机，0x55=关机
#       省略：Byte3(SBIT24~31保留), Bit34~63(保留)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
msgs.append({
    'id':   0x0C0A88EF,
    'name': 'Rx0_0x0C0A88EF',
    'dlc':  8,
    'tx':   NODE1,
    'rx':   NODE2,
    'rate': '100ms',
    'desc': 'VCU Auxiliary Controller enable 辅驱开关机控制（油泵/气泵/DCDC共用帧）',
    'sigs': [
        sig('VCU_OilPump_CtrlCmd',   0,  8, 1, 0, 0, 255, '',
            'Oil pump control 油泵指令 0xAA=开机 0x55=关机'),
        sig('VCU_AirPump_CtrlCmd',   8,  8, 1, 0, 0, 255, '',
            'Air pump control 气泵指令 0xAA=开机 0x55=关机'),
        sig('VCU_DCDC_CtrlCmd',     16,  8, 1, 0, 0, 255, '',
            'DC-DC control DCDC指令 0xAA=开机 0x55=关机'),
        # Byte3 (SBIT=24, LEN=8): 保留 → 省略
        sig('VCU_OilPump_HiTmpLmt', 32,  1, 1, 0, 0, 1, '',
            '油泵电机高温限功信号 0=正常 1=激活'),
        sig('VCU_OilPump_HiTmpStp', 33,  1, 1, 0, 0, 1, '',
            '油泵电机高温停机信号 0=正常 1=激活'),
        # SBIT=34~63 (30bit): 保留 → 省略
    ]
})

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Tx1  EHPS→VCU  状态报文1  ID=0x1801A79B  100ms
# 说明：电压/电流/温度/故障代码
#       故障代码 Byte7(SBIT=56~63) 逐位展开
#       Bit3(SBIT=59)标注"此位不能查询" → 省略
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
msgs.append({
    'id':   0x1801A79B,
    'name': 'Tx1_0x1801A79B',
    'dlc':  8,
    'tx':   NODE2,
    'rx':   NODE1,
    'rate': '100ms',
    'desc': 'EHPS DC/AC Status1 输入输出电压电流/控制器温度/故障位',
    'sigs': [
        # ── 模拟量 ─────────────────────────────────────────────────────────
        # factor=1, offset=0, 物理0~1000V → 总线MIN=0, MAX=1000
        sig('EHPS_InputVolt',        0, 16, 1,   0,   0, 1000, 'V',
            'Input voltage 输入电压'),
        sig('EHPS_OutputVolt',      16, 16, 1,   0,   0, 1000, 'V',
            'Output voltage 输出电压'),
        # factor=0.1, offset=0, 物理0~100A → 总线MAX=100/0.1=1000
        sig('EHPS_OutputCurr',      32, 16, 0.1, 0,   0, 1000, 'A',
            'Output current 输出电流'),
        # factor=1, offset=-40, 物理-40~210℃ → 总线MIN=0, MAX=(210+40)=250
        sig('EHPS_CtrlTemp',        48,  8, 1,  -40,  0,  250, '℃',
            'DC/AC controller temperature 油泵控制器温度'),
        # ── 故障代码 Byte7(SBIT=56) 逐位展开，Bit3省略 ─────────────────────
        sig('EHPS_FaultUnderVolt',  56,  1, 1,   0,   0,    1, '',
            '输入欠压故障 0=正常 1=故障'),
        sig('EHPS_FaultOverVolt',   57,  1, 1,   0,   0,    1, '',
            '输入过压故障 0=正常 1=故障'),
        sig('EHPS_FaultLVPower',    58,  1, 1,   0,   0,    1, '',
            '低压电源故障 0=正常 1=故障'),
        # SBIT=59 (Bit3): 文档注明"此位不能查询" → 省略
        sig('EHPS_FaultOverHeat',   60,  1, 1,   0,   0,    1, '',
            '过热故障 0=正常 1=故障'),
        sig('EHPS_FaultShortCkt',   61,  1, 1,   0,   0,    1, '',
            '短路故障 0=正常 1=故障'),
        sig('EHPS_FaultOverLoad',   62,  1, 1,   0,   0,    1, '',
            '过载故障 0=正常 1=故障'),
        sig('EHPS_FaultPhaseLoss',  63,  1, 1,   0,   0,    1, '',
            '缺相故障 0=正常 1=故障'),
    ]
})

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Tx2  EHPS→VCU  状态报文2  ID=0x1811A79B  100ms
# 说明：U相电压电流/运行状态/切断状态/故障等级/DC输入电流
#       省略：SBIT=38~47 (10bit保留)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
msgs.append({
    'id':   0x1811A79B,
    'name': 'Tx2_0x1811A79B',
    'dlc':  8,
    'tx':   NODE2,
    'rx':   NODE1,
    'rate': '100ms',
    'desc': 'EHPS DC/AC Status2 U相/运行状态/故障等级/DC输入电流',
    'sigs': [
        sig('EHPS_OutU_Volt',        0, 16, 1,   0,   0, 1000, 'V',
            'Inverter output U-phase voltage 油泵逆变器输出U相电压'),
        # factor=0.1, offset=0, 物理0~100A → 总线MAX=1000
        sig('EHPS_OutU_Curr',       16, 16, 0.1, 0,   0, 1000, 'A',
            'Inverter output U-phase current 油泵逆变器输出U相电流'),
        sig('EHPS_DcAcStatus',      32,  2, 1,   0,   0,    3, '',
            'DC/AC pump status 油泵状态 0=停机 1=预充电中 2=预充电完成 3=运行'),
        sig('EHPS_OutputCutoff',    34,  2, 1,   0,   0,    3, '',
            'Output cutoff 输出切断 0=无效 1=有效 2=错误 3=无定义'),
        sig('EHPS_InputCutoff',     36,  2, 1,   0,   0,    3, '',
            'Input cutoff 输入切断 0=无效 1=有效 2=错误 3=无定义'),
        # SBIT=38~47 (10bit): 保留 → 省略
        sig('EHPS_FaultGrade',      48,  3, 1,   0,   0,    4, '',
            'Fault grade 故障等级 0=无故障 1=一级(警告降额) 2=二级 3=三级 4=四级(最高停车)'),
        # factor=0.1, offset=0, 物理0~100A, LEN=13bit → 总线MAX=1000
        sig('EHPS_InputCurrDC',     51, 13, 0.1, 0,   0, 1000, 'A',
            'Input current DC 直流输入电流'),
    ]
})

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Tx3  EHPS→VCU  状态报文3  ID=0x1821A79B  100ms
# 说明：V/W相电压电流（无保留位）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
msgs.append({
    'id':   0x1821A79B,
    'name': 'Tx3_0x1821A79B',
    'dlc':  8,
    'tx':   NODE2,
    'rx':   NODE1,
    'rate': '100ms',
    'desc': 'EHPS DC/AC Status3 V相/W相电压电流',
    'sigs': [
        sig('EHPS_OutV_Volt',        0, 16, 1,   0,   0, 1000, 'V',
            'Inverter output V-phase voltage 油泵逆变器输出V相电压'),
        sig('EHPS_OutV_Curr',       16, 16, 0.1, 0,   0, 1000, 'A',
            'Inverter output V-phase current 油泵逆变器输出V相电流'),
        sig('EHPS_OutW_Volt',       32, 16, 1,   0,   0, 1000, 'V',
            'Inverter output W-phase voltage 油泵逆变器输出W相电压'),
        sig('EHPS_OutW_Curr',       48, 16, 0.1, 0,   0, 1000, 'A',
            'Inverter output W-phase current 油泵逆变器输出W相电流'),
    ]
})

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Tx4  EHPS→VCU  状态报文4  ID=0x1831A79B  500ms
# 说明：电机转速/输出频率/电机转矩
#       省略：Byte6~7(SBIT=48~63保留)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
msgs.append({
    'id':   0x1831A79B,
    'name': 'Tx4_0x1831A79B',
    'dlc':  8,
    'tx':   NODE2,
    'rx':   NODE1,
    'rate': '500ms',
    'desc': 'EHPS DC/AC Status4 电机转速/输出频率/电机转矩',
    'sigs': [
        # factor=1, offset=-15000, 物理-15000~15000rpm
        # 总线MIN = (-15000-(-15000))/1 = 0
        # 总线MAX = (15000-(-15000))/1  = 30000
        sig('EHPS_MotorSpeed',       0, 16, 1,   -15000, 0, 30000, 'rpm',
            'Motor speed 电机转速 物理值=-15000~15000rpm'),
        # factor=0.01, offset=0, 物理0~600Hz → 总线MAX=600/0.01=60000
        sig('EHPS_OutFreq',         16, 16, 0.01,    0,  0, 60000, 'Hz',
            'Output frequency 输出频率 物理值0~600Hz'),
        # factor=1, offset=0, 物理0~500Nm → 总线MAX=500
        sig('EHPS_MotorTorque',     32, 16, 1,        0,  0,   500, 'Nm',
            'Motor torque 电机转矩 物理值0~500Nm'),
        # SBIT=48~63 (16bit): 保留 → 省略
    ]
})


# ─── JSON5 生成（通常不需要修改以下代码） ────────────────────────────────────

def build_json5(msgs, node1, node2, source_doc):
    total_sigs = sum(len(m['sigs']) for m in msgs)
    rx_count   = sum(1 for m in msgs if m['tx'] == node1)
    tx_count   = len(msgs) - rx_count

    lines = ['{']
    lines.append(f'    // {node2} CAN 报文定义 — 已省略所有保留位，故障代码逐位展开')
    lines.append(f'    // 来源：{source_doc}')
    lines.append(f'    // 协议：SAE J1939，CAN 2.0B，29位扩展帧，250Kbs，Intel字节序（默认）')
    lines.append(f'    // 统计：共{len(msgs)}条报文({rx_count}Rx+{tx_count}Tx)，{total_sigs}个有效信号')
    lines.append(f'')
    lines.append(f'    NODE1: "{node1}",')
    lines.append(f'    NODE2: "{node2}",')
    lines.append(f'    MSGS: [')
    lines.append(SEP)

    for m in msgs:
        lines.append(f'    // [{m["rate"]}] {m["desc"]}')
        lines.append(
            f'    {{ID: {fmt_id(m["id"])}, MSGNAME: "{m["name"]}", DLC: {m["dlc"]}, '
            f'TXNODE:"{m["tx"]}", RXNODE:"{m["rx"]}", SIGS:['
        )
        for s in m['sigs']:
            lines.append(s)
        lines.append('    ]},')
        lines.append(SEP)

    lines.append('    ]')
    lines.append('}')
    return '\n'.join(lines)


if __name__ == '__main__':
    content = build_json5(msgs, NODE1, NODE2, SOURCE_DOC)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write(content)
    total = sum(len(m['sigs']) for m in msgs)
    print(f'✓ 生成完成：{OUTPUT_PATH}')
    print(f'  共 {len(msgs)} 条报文，{total} 个有效信号（保留位已省略）')
