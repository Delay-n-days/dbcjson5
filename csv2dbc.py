#!/usr/bin/env python
"""从统一的 CSV 表生成 DBC 文件"""

import csv
import json
import cantools
from pathlib import Path


def parse_json_comment(json_str):
    """解析 JSON 格式的注释"""
    if not json_str or json_str.strip() == '':
        return None
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return None


def build_comment_text(key_value_dict):
    """将键值对字典转换为注释文本"""
    if isinstance(key_value_dict, dict):
        lines = []
        for key, value in key_value_dict.items():
            if key.isdigit():
                lines.append(f"{key} = {value}")
            else:
                lines.append(f"{value}")
        return '\n'.join(lines)
    return str(key_value_dict)


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
                    
                    messages_dict[msg_id] = {
                        'frame_id': msg_id_int,
                        'name': row['消息名称'],
                        'length': int(row['消息长度']),
                        'sender': row['发送者'] if row['发送者'] else 'Vector__XXX',
                        'comment': row.get('消息备注(JSON)', ''),
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
                    'comment': row.get('信号备注(JSON)', '')
                }
                
                messages_dict[msg_id]['signals'].append(signal_info)
        
        # 使用 cantools 生成 DBC
        # 优先使用原始 DBC 作为模板，如果不存在则从 CSV 数据构建
        original_dbc_path = 'LvKong_1C_V2.5_A484_A485_100_00B.dbc'
        
        if Path(original_dbc_path).exists():
            print(f"使用原始 DBC 文件作为模板: {original_dbc_path}")
            db = cantools.database.load_file(original_dbc_path, encoding='gb2312')
        else:
            print(f"警告: 原始 DBC 文件不存在，从 CSV 数据构建数据库")
            # 从 CSV 数据构建 cantools 数据库对象
            db = cantools.database.Database()
            
            for msg_id, msg_data in messages_dict.items():
                signals = []
                for sig_info in msg_data['signals']:
                    signal = cantools.database.Signal(
                        name=sig_info['name'],
                        start=sig_info['start'],
                        length=sig_info['length'],
                        byte_order=sig_info['byte_order'],
                        is_signed=sig_info['is_signed'],
                        scale=sig_info['scale'],
                        offset=sig_info['offset'],
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
                db.add_message(message)
        
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
        
        if len(db_verify.messages) == len(messages_dict):
            print(f"✓ 验证成功! 包含 {len(messages_dict)} 条消息")
        else:
            print(f"⚠ 警告: 消息数量不匹配")
        
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


if __name__ == '__main__':
    unified_csv = 'outputs/LvKong_1C_V2.5_A484_A485_100_00B_unified.csv'
    output_dbc = 'outputs/LvKong_1C_V2.5_A484_A485_100_00B_from_unified.dbc'
    
    success = unified_csv_to_dbc(unified_csv, output_dbc)
    if not success:
        import sys
        sys.exit(1)

