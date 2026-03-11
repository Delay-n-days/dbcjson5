#!/usr/bin/env python
"""从统一的 CSV 表生成 DBC 文件"""

import csv
import json
import sys
from pathlib import Path
from typing import Optional

import cantools
import typer
from cantools.database.conversion import LinearConversion

app = typer.Typer(help="CSV 到 DBC 文件转换工具")


def parse_json_comment(json_str):
    """解析 JSON 格式的注释"""
    if not json_str or json_str.strip() == '':
        return None
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return None


def is_binary_string(s):
    """检查字符串是否为二进制形式 (00, 01, 10, 11 等)"""
    if not s:
        return False
    # 检查是否全由 0 和 1 组成
    return all(c in '01' for c in s) and len(s) > 0


def build_comment_text(key_value_dict):
    """
    将键值对字典转换为注释文本
    - 如果 key 是纯数字，格式为：key = value
    - 如果 key 是二进制字符串，格式为：key:value
    - 如果是 description 等其他字段，保持原文本
    """
    if isinstance(key_value_dict, dict):
        # 检查是否只有 description 字段
        if len(key_value_dict) == 1 and 'description' in key_value_dict:
            return key_value_dict['description']
        
        lines = []
        for key, value in key_value_dict.items():
            if key == 'description':
                # skip description field in multi-line comments
                continue
            elif is_binary_string(key):
                # 二进制字符串格式：00:空档位
                lines.append(f"{key}:{value}")
            elif key.isdigit():
                # 纯数字格式：0 = Ready
                lines.append(f"{key} = {value}")
            else:
                # 其他格式：仅输出 value
                lines.append(f"{value}")
        
        return '\n'.join(lines) if lines else str(key_value_dict)
    return str(key_value_dict)


def _process_signal_comment(comment_str):
    """
    处理信号注释，将 JSON 格式转换为 DBC 格式
    """
    # print(f"正在处理信号注释: {comment_str}")
    if not comment_str or comment_str.strip() == '':
        return ''
    
    # 尝试解析为 JSON
    parsed = parse_json_comment(comment_str)
    if parsed and isinstance(parsed, dict):
        # 转换为 DBC 格式
        return build_comment_text(parsed)
    
    # 打印调试信息
    print(f"⚠ 无法解析的注释格式，保留原文本: {comment_str}", file=sys.stderr)
    # 如果不是 JSON，直接返回原文本
    return comment_str


def unified_csv_to_dbc(unified_csv, output_dbc, encoding='utf-8'):
    """
    从统一的 CSV 表生成 DBC 文件
    
    Args:
        unified_csv: 统一 CSV 文件路径
        output_dbc: 输出 DBC 文件路径
        encoding: 输入 CSV 编码
    """
    
    unified_csv_path = Path(unified_csv)
    
    if not unified_csv_path.exists():
        print(f"错误: 文件 {unified_csv} 不存在")
        return False
    
    try:
        # 从统一 CSV 读取数据
        messages_dict = {}
        senders = set()
        
        print(f"正在读取统一 CSV: {unified_csv}")
        with open(unified_csv_path, 'r', encoding=encoding) as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                msg_id = row['消息ID']
                
                # 如果是新消息，创建消息对象
                if msg_id not in messages_dict:
                    msg_id_int = int(msg_id, 16) if msg_id.startswith('0x') else int(msg_id)
                    is_extended = msg_id_int > 0x7FF
                    
                    # 构建 comment，包含周期信息
                    comment = row.get('消息备注(JSON)', '')
                    period = row.get('周期时间(ms)', '').strip()
                    if period:
                        period_text = f"period {period}ms"
                        comment = f"{period_text}\n{comment}" if comment else period_text
                    
                    messages_dict[msg_id] = {
                        'frame_id': msg_id_int,
                        'name': row['消息名称'],
                        'length': int(row['消息长度']),
                        'sender': row['发送者'] if row['发送者'] else 'Vector__XXX',
                        'comment': comment,
                        'is_extended': is_extended,
                        'signals': []
                    }
                    
                    if row['发送者']:
                        senders.add(row['发送者'])
                
                # 构建信号对象
                is_signed = row.get('有符号', '否') == '是'
                byte_order = 'little_endian' if row.get('字节序', '') == 'little_endian' else 'big_endian'
                
                try:
                    minimum = float(row['最小值']) if row.get('最小值', '') else None
                except (ValueError, KeyError):
                    minimum = None
                
                try:
                    maximum = float(row['最大值']) if row.get('最大值', '') else None
                except (ValueError, KeyError):
                    maximum = None
                
                signal_info = {
                    'name': row['信号名称'],
                    'start': int(row['起始位']),
                    'length': int(row['长度(bit)']),
                    'is_signed': is_signed,
                    'scale': float(row['缩放系数']),
                    'offset': float(row['偏移']),
                    'minimum': minimum,
                    'maximum': maximum,
                    'unit': row.get('单位', '') if row.get('单位', '') else '',
                    'receivers': [r.strip() for r in row.get('接收者', '').split(',') if r.strip()],
                    'byte_order': byte_order,
                    'comment': _process_signal_comment(row.get('备注(JSON)', ''))
                }
                
                messages_dict[msg_id]['signals'].append(signal_info)
        
        # 使用 cantools 生成 DBC
        # 优先使用原始 DBC 作为模板，如果不存在则从 CSV 数据构建

        # 从 CSV 数据构建 cantools 数据库对象
        db = cantools.database.Database()
        
        for msg_id, msg_data in messages_dict.items():
            signals = []
            for sig_info in msg_data['signals']:
                # 创建线性转换对象（用于 scale 和 offset）
                # 根据长度判断是否是浮点数（32位或64位认为可能是浮点）
                is_float_signal = sig_info['length'] in (32, 64)
                conversion = LinearConversion(
                    scale=sig_info['scale'],
                    offset=sig_info['offset'],
                    is_float=is_float_signal
                ) if (sig_info['scale'] != 1 or sig_info['offset'] != 0) else None
                
                signal = cantools.database.Signal(
                    name=sig_info['name'],
                    start=sig_info['start'],
                    length=sig_info['length'],
                    byte_order=sig_info['byte_order'],
                    is_signed=sig_info['is_signed'],
                    conversion=conversion,
                    minimum=sig_info['minimum'],
                    maximum=sig_info['maximum'],
                    unit=sig_info['unit'],
                    receivers=sig_info['receivers'],
                    comment=sig_info['comment']
                )
                signals.append(signal)
            
            message = cantools.database.Message(
                frame_id=msg_data['frame_id'],
                name=msg_data['name'],
                length=msg_data['length'],
                signals=signals,
                senders=[msg_data['sender']],
                comment=msg_data['comment'],
                is_extended_frame=msg_data['is_extended']
            )
            db.messages.append(message)
        
        # 输出 DBC 文件
        output_path = Path(output_dbc)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"正在生成 DBC 文件...")
        dbc_content = db.as_dbc_string()
        
        print(f"正在写入 DBC 文件: {output_dbc}")
        with open(output_path, 'w', encoding='gb2312') as f:
            f.write(dbc_content)
        
        # 验证
        print(f"正在验证生成的 DBC 文件...")
        db_verify = cantools.database.load_file(str(output_path), encoding='gb2312')

        # 打印信息数量和信号数量和带注释的数量
        print(f"✓ 消息数量: {len(db_verify.messages)}")
        total_signals = sum(len(msg.signals) for msg in db_verify.messages)
        print(f"✓ 信号数量: {total_signals}")
        commented_signals = sum(1 for msg in db_verify.messages for sig in msg.signals if sig.comment and sig.comment.strip() != '')
        print(f"✓ 带注释的信号数量: {commented_signals}")
        
        print(f"✓ 输出文件: {output_dbc}")
        return True
        
    except FileNotFoundError as e:
        print(f"文件错误: {e}")
        return False
    except (ValueError, KeyError) as e:
        print(f"数据错误: {e}")
        import traceback
        traceback.print_exc()
        return False


@app.command()
def convert(
    unified_csv: str = typer.Argument(
        ...,
        help="统一 CSV 文件路径"
    ),
    output_dbc: str | None = typer.Option(
        None,
        "--output",
        "-o",
        help="输出 DBC 文件路径，默认为 outputs/{csv_name}_from_unified.dbc"
    ),
    encoding: str = typer.Option(
        "gb2312",
        "--encoding",
        "-e",
        help="CSV 文件编码，默认为 gb2312"
    ),
):
    """
    从统一的 CSV 表生成 DBC 文件
    
    \b
    示例:
        python csv2dbc.py "outputs/LvKong_1C_V2.5_A484_A485_100_00B_unified.csv"
        python csv2dbc.py "data.csv" -o "output.dbc" -e utf-8
    """
    # 如果没有指定输出文件，自动生成
    if not output_dbc:
        csv_name = Path(unified_csv).stem
        output_dbc = f"outputs/{csv_name}_from_unified.dbc"
    
    try:
        success = unified_csv_to_dbc(unified_csv, output_dbc, encoding=encoding)
        if not success:
            raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"❌ 转换失败: {e}", err=True)
        raise typer.Exit(code=1)


@app.command()
def version():
    """显示版本信息"""
    typer.echo("csv2dbc v2.0")
    typer.echo("CSV 到 DBC 文件转换工具")


if __name__ == "__main__":
    app()

