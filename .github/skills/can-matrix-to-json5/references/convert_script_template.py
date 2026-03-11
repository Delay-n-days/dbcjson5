"""
CAN Matrix Excel → JSON5 转换脚本模板
======================================
使用前请替换：
  - XLSX_PATH     : Excel 文件路径
  - NODE1_NAME    : 主控节点名称（如 "VDCU"）
  - NODE1_COL     : NODE1 在 Matrix sheet 中的列索引
  - NODE2_NAME    : 目标节点名称（如 "HVASAirPump"）
  - NODE2_COL     : NODE2 在 Matrix sheet 中的列索引
  - OUTPUT_PATH   : 输出 JSON5 文件路径
"""

import pandas as pd
import re

# ─── 配置区（使用前必须修改） ────────────────────────────────────────────────
XLSX_PATH   = "/mnt/user-data/uploads/YOUR_FILE.xlsx"
NODE1_NAME  = "VDCU"
NODE1_COL   = 36          # 通过探索确认，不同项目可能不同
NODE2_NAME  = "HVASAirPump"
NODE2_COL   = 50          # 通过探索确认
OUTPUT_PATH = f"/mnt/user-data/outputs/{NODE1_NAME}_{NODE2_NAME}_CAN_Matrix.json5"
SHEET_NAME  = "Matrix"    # 通常固定为 "Matrix"
# ─────────────────────────────────────────────────────────────────────────────


def explore_columns(df):
    """打印列索引与列名，用于确认节点列位置。"""
    print("=== 列索引探索 ===")
    for j in range(df.shape[1]):
        raw = str(df.iloc[0, j]).replace('\n', '\\n')
        print(f"  Col {j:3d}: {raw}")


def safe_int(val, default=0):
    try:
        return int(float(val)) if pd.notna(val) else default
    except Exception:
        return default


def safe_float(val, default=1.0):
    try:
        return float(val) if pd.notna(val) else default
    except Exception:
        return default


def safe_hex(val, default=0):
    """将形如 '0xFF' 或 '0x00FF' 的字符串解析为整数。"""
    try:
        if pd.notna(val):
            s = str(val).strip()
            if s.startswith('0x') or s.startswith('0X'):
                return int(s, 16)
            return int(s)
        return default
    except Exception:
        return default


def safe_str(val):
    if pd.notna(val):
        s = str(val).strip()
        if s not in ['nan', '']:
            return s.replace('\n', ' ')
    return ''


def format_id(raw_id_str):
    """
    将原始 ID 字符串格式化为 0x 开头的 8 位大写十六进制。
    例如：'0x18FF5227x' → '0x18FF5227'
         '018FEC117'    → '0x18FEC117'
    """
    s = str(raw_id_str).strip()
    # 去掉末尾的 x（有些项目在末尾加 x 表示扩展帧）
    s = s.rstrip('x').rstrip('X')
    # 去掉 0x 前缀后解析
    s = s.lstrip('0x').lstrip('0X') or '0'
    val = int(s, 16)
    return f'0x{val:08X}'


def parse_signal(row):
    """从信号行提取所有信号属性。"""
    factor = safe_float(row[18], 1.0)
    factor_out = int(factor) if factor == int(factor) else factor

    offset = safe_float(row[19], 0.0)
    offset_out = int(offset) if offset == int(offset) else offset

    # MIN/MAX 优先使用 Hex 列（总线原始值），比物理值更精确
    min_hex = safe_hex(row[22], 0)
    max_hex = safe_hex(row[23], 0)

    # 如果 Hex 列为 0（可能是空或真的是0），回退到物理值列
    # 注意：物理值需要自行换算，这里仅作为后备
    if max_hex == 0 and pd.notna(row[21]):
        try:
            phys_max = float(row[21])
            # 不直接换算，只是提示可能有问题
        except Exception:
            pass

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


def determine_tx_rx(msg, node1_name, node2_name):
    """
    根据 node1_role 和 node2_role 确定 TX/RX 节点。
    返回 (txnode, rxnode) 字符串元组。
    """
    n1 = msg['node1_role']
    n2 = msg['node2_role']

    if n1 == 'S' and n2 == 'R':
        return node1_name, node2_name
    elif n1 == 'R' and n2 == 'S':
        return node2_name, node1_name
    elif n1 == 'R' and n2 == 'R':
        # 双方均为接收，根据报文名前缀推断发送方
        prefix = msg['name'].split('_')[0] if '_' in msg['name'] else msg['name']
        return prefix, f"{node1_name}/{node2_name}"
    else:
        # 其他情况（如 S/S 极罕见），按 node1 发送处理
        return node1_name, node2_name


def msgname_prefix(txnode, node1_name, node2_name, idx):
    """
    从 NODE2 视角命名：NODE2 接收的报文叫 Rx，发送的叫 Tx。
    """
    if txnode == node2_name:
        return f"Tx{idx}"
    else:
        return f"Rx{idx}"


def format_sig_line(s):
    """生成单行信号的 JSON5 文本。"""
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


def build_json5(relevant_msgs, node1_name, node2_name):
    """将筛选后的报文列表生成完整 JSON5 字符串。"""
    SEP = '// +' + '-' * 118 + '+'
    HEADER = (
        '// | ID    MSGNAME   DLC  TXNODE   RXNODE   '
        'SIGS    SIG      SBIT   LEN      FACTOR  OFFSET  MIN   MAX    UINT  COMMENT |'
    )

    lines = []
    lines.append('{')
    lines.append(f'    NODE1: "{node1_name}",')
    lines.append(f'    NODE2: "{node2_name}",')
    lines.append('    MSGS: [')
    lines.append(SEP)
    lines.append(HEADER)
    lines.append(SEP)

    for idx, msg in enumerate(relevant_msgs):
        msg_id = format_id(msg['id_raw'])
        txnode, rxnode = determine_tx_rx(msg, node1_name, node2_name)
        prefix = msgname_prefix(txnode, node1_name, node2_name, idx)
        msgname = f"{prefix}_{msg_id}"

        lines.append('')
        lines.append(
            f'    {{ID: {msg_id}, MSGNAME: "{msgname}", '
            f'DLC: {msg["dlc"]}, TXNODE:"{txnode}", RXNODE:"{rxnode}", SIGS:['
        )
        for sig in msg['sigs']:
            lines.append(format_sig_line(sig))
        lines.append('    ]},')
        lines.append(SEP)

    lines.append('    ]')
    lines.append('}')
    return '\n'.join(lines)


def main():
    # 1. 读取 Excel
    df = pd.read_excel(XLSX_PATH, sheet_name=SHEET_NAME, header=None)
    print(f"Matrix shape: {df.shape}")

    # 2. （可选）探索列索引，确认 NODE 列位置
    # explore_columns(df)

    # 3. 遍历行，收集报文和信号
    messages = []
    current_msg = None

    for i, row in df.iterrows():
        if i == 0:
            continue  # 跳过表头行

        msg_name_val = row[0]
        if pd.notna(msg_name_val) and str(msg_name_val).strip() not in ['nan', '']:
            # 报文行
            n1_val = str(row[NODE1_COL]).strip() if pd.notna(row[NODE1_COL]) else ''
            n2_val = str(row[NODE2_COL]).strip() if pd.notna(row[NODE2_COL]) else ''

            current_msg = {
                'name': str(msg_name_val).strip(),
                'id_raw': str(row[2]).strip() if pd.notna(row[2]) else '',
                'dlc': safe_int(row[8], 8),
                'node1_role': n1_val,
                'node2_role': n2_val,
                'relevant': (n1_val in ['S', 'R']) and (n2_val in ['S', 'R']),
                'sigs': [],
            }
            messages.append(current_msg)

        sig_name_val = row[9]
        if (pd.notna(sig_name_val)
                and str(sig_name_val).strip() not in ['nan', '']
                and current_msg is not None):
            # 信号行
            current_msg['sigs'].append(parse_signal(row))

    # 4. 筛选目标报文
    relevant = [m for m in messages if m['relevant']]
    print(f"总报文数: {len(messages)}，筛选出 {NODE1_NAME}<->{NODE2_NAME} 相关报文: {len(relevant)} 条")
    for m in relevant:
        txnode, rxnode = determine_tx_rx(m, NODE1_NAME, NODE2_NAME)
        print(f"  {m['name']:<30} ID:{m['id_raw']:<15} TX:{txnode:<15} RX:{rxnode:<15} Sigs:{len(m['sigs'])}")

    # 5. 生成 JSON5
    json5_content = build_json5(relevant, NODE1_NAME, NODE2_NAME)

    # 6. 写出文件
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write(json5_content)
    print(f"\n输出完成：{OUTPUT_PATH}")


if __name__ == '__main__':
    main()
