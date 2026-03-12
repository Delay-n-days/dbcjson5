#!/usr/bin/env python
"""从 DBC 文件生成统一 CSV 格式"""

import csv
import json
import sys
from pathlib import Path
from typing import Optional

import cantools
import typer

app = typer.Typer(help="DBC 到 CSV 文件转换工具")


def parse_comment_to_json(comment: str) -> str:
    """
    将 DBC 注释转换为 JSON 格式
    
    支持以下格式：
    - 0 = Ready (数字枚举)
    - 00:空档位 (二进制枚举)
    - 纯文本描述
    """
    if not comment or comment.strip() == '':
        return ''
    
    lines = comment.strip().split('\n')
    
    # 检查是否包含枚举值
    enum_dict = {}
    description_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # 检查 "key = value" 格式
        if ' = ' in line:
            parts = line.split(' = ', 1)
            if len(parts) == 2:
                key = parts[0].strip()
                value = parts[1].strip()
                enum_dict[key] = value
                continue
        
        # 检查 "key:value" 格式（二进制或数字）
        if ':' in line and not line.startswith('//'):
            parts = line.split(':', 1)
            if len(parts) == 2:
                key = parts[0].strip()
                value = parts[1].strip()
                # 检查是否是枚举（key 是数字或二进制字符串）
                if key.isdigit() or all(c in '01' for c in key):
                    enum_dict[key] = value
                    continue
        
        # 否则作为描述
        description_lines.append(line)
    
    # 构建 JSON
    if enum_dict and description_lines:
        # 既有枚举又有描述
        result = enum_dict.copy()
        result['description'] = '\n'.join(description_lines)
        return json.dumps(result, ensure_ascii=False)
    elif enum_dict:
        # 只有枚举
        return json.dumps(enum_dict, ensure_ascii=False)
    elif description_lines:
        # 只有描述
        return json.dumps({'description': '\n'.join(description_lines)}, ensure_ascii=False)
    
    return ''


def extract_period_from_comment(comment: str) -> tuple[str, str]:
    """
    从注释中提取周期信息
    
    Returns:
        (period, remaining_comment)
    """
    if not comment:
        return '', ''
    
    lines = comment.strip().split('\n')
    period = ''
    remaining_lines = []
    
    for line in lines:
        line_stripped = line.strip()
        # 检查是否是周期信息
        if line_stripped.lower().startswith('period ') and 'ms' in line_stripped.lower():
            # 提取周期值
            period_part = line_stripped.lower().replace('period', '').replace('ms', '').strip()
            period = period_part
        else:
            remaining_lines.append(line)
    
    remaining_comment = '\n'.join(remaining_lines).strip()
    return period, remaining_comment


def dbc_to_unified_csv(dbc_file: str, output_csv: str, encoding: str = 'utf-8'):
    """
    从 DBC 文件生成统一 CSV 格式
    
    Args:
        dbc_file: DBC 文件路径
        output_csv: 输出 CSV 文件路径
        encoding: DBC 文件编码
    """
    dbc_path = Path(dbc_file)
    
    if not dbc_path.exists():
        print(f"错误: 文件 {dbc_file} 不存在")
        return False
    
    try:
        # 读取 DBC 文件
        print(f"正在读取 DBC 文件: {dbc_file}")
        db = cantools.database.load_file(str(dbc_path), encoding=encoding)
        
        # 准备 CSV 数据
        csv_rows = []
        
        print(f"正在转换为统一 CSV 格式...")
        for message in db.messages:
            # 提取消息信息
            # 格式化消息ID，保持8位十六进制格式
            if message.is_extended_frame:
                msg_id = f"0x{message.frame_id:08X}"
            else:
                msg_id = f"0x{message.frame_id:X}"
            msg_name = message.name
            msg_length = message.length
            
            # 提取周期和注释
            period, msg_comment_cleaned = extract_period_from_comment(message.comment or '')
            msg_comment_json = parse_comment_to_json(msg_comment_cleaned)
            
            # 发送者
            sender = message.senders[0] if message.senders else ''
            
            # 处理每个信号
            for signal in message.signals:
                # 获取 scale 和 offset（转换为整数或保持浮点数）
                scale = 1
                offset = 0
                if signal.scale is not None:
                    scale = signal.scale
                    # 如果是整数值，转换为整数
                    if scale == int(scale):
                        scale = int(scale)
                
                if signal.offset is not None:
                    offset = signal.offset
                    # 如果是整数值，转换为整数
                    if offset == int(offset):
                        offset = int(offset)
                
                # 字节序
                byte_order = signal.byte_order
                
                # 有符号
                is_signed = '是' if signal.is_signed else '否'
                
                # 单位
                unit = signal.unit or ''
                
                # 接收者
                receivers = ', '.join(signal.receivers) if signal.receivers else ''
                
                # 注释
                signal_comment_json = parse_comment_to_json(signal.comment or '')
                
                # 最小值和最大值（转换为整数或保持浮点数）
                minimum = ''
                if signal.minimum is not None:
                    # 如果是整数值，转换为整数
                    if signal.minimum == int(signal.minimum):
                        minimum = int(signal.minimum)
                    else:
                        minimum = signal.minimum
                
                maximum = ''
                if signal.maximum is not None:
                    # 如果是整数值，转换为整数
                    if signal.maximum == int(signal.maximum):
                        maximum = int(signal.maximum)
                    else:
                        maximum = signal.maximum
                
                # 初值（DBC 中通常没有，留空）
                initial_value = ''
                
                # 构建行
                row = {
                    '消息ID': msg_id,
                    '消息名称': msg_name,
                    '消息长度': msg_length,
                    '周期时间(ms)': period,
                    '发送者': sender,
                    '消息备注(JSON)': msg_comment_json,
                    '信号名称': signal.name,
                    '起始位': signal.start,
                    '长度(bit)': signal.length,
                    '字节序': byte_order,
                    '有符号': is_signed,
                    '初值': initial_value,
                    '缩放系数': scale,
                    '偏移': offset,
                    '最小值': minimum,
                    '最大值': maximum,
                    '单位': unit,
                    '接收者': receivers,
                    '备注(JSON)': signal_comment_json
                }
                
                csv_rows.append(row)
        
        # 写入 CSV 文件
        output_path = Path(output_csv)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"正在写入 CSV 文件: {output_csv}")
        fieldnames = [
            '消息ID', '消息名称', '消息长度', '周期时间(ms)', '发送者', '消息备注(JSON)',
            '信号名称', '起始位', '长度(bit)', '字节序', '有符号', '初值', 
            '缩放系数', '偏移', '最小值', '最大值', '单位', '接收者', '备注(JSON)'
        ]
        
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_rows)
        
        # 统计
        total_messages = len(db.messages)
        total_signals = len(csv_rows)
        
        print(f"✓ 消息数量: {total_messages}")
        print(f"✓ 信号数量: {total_signals}")
        print(f"✓ 输出文件: {output_csv}")
        
        return True
        
    except FileNotFoundError as e:
        print(f"文件错误: {e}")
        return False
    except Exception as e:
        print(f"转换错误: {e}")
        import traceback
        traceback.print_exc()
        return False


@app.command()
def convert(
    dbc_file: str = typer.Argument(
        ...,
        help="DBC 文件路径"
    ),
    output_csv: Optional[str] = typer.Option(
        None,
        "--output",
        "-o",
        help="输出 CSV 文件路径，默认为 outputs/{dbc_name}_from_dbc.csv"
    ),
    encoding: str = typer.Option(
        "gb2312",
        "--encoding",
        "-e",
        help="DBC 文件编码，默认为 gb2312"
    ),
):
    """
    从 DBC 文件生成统一 CSV 格式
    
    \b
    示例:
        python dbc2csv.py convert "outputs/GTAKE_motor_250K.dbc" -e gb2312
        python dbc2csv.py convert "data.dbc" -o "output.csv" -e utf-8
    """
    # 如果没有指定输出文件，自动生成
    if not output_csv:
        dbc_name = Path(dbc_file).stem
        output_csv = f"outputs/{dbc_name}_from_dbc.csv"
    
    try:
        success = dbc_to_unified_csv(dbc_file, output_csv, encoding=encoding)
        if not success:
            raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"❌ 转换失败: {e}", err=True)
        raise typer.Exit(code=1)


@app.command()
def version():
    """显示版本信息"""
    typer.echo("dbc2csv v1.0")
    typer.echo("DBC 到 CSV 文件转换工具")


if __name__ == "__main__":
    app()
