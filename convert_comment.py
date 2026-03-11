#!/usr/bin/env python
"""将 CSV 中 comment 中的 'lines' 格式转换为键值对格式"""

import csv
import json
import re
from pathlib import Path

def convert_lines_to_dict(comment_str):
    """
    将 {"lines": ["00:空档位", "01：前进档位", "10：后退档位"]} 
    转换为 {"0": "空档位", "1": "前进档位", "2": "后退档位"}
    """
    if not comment_str or 'lines' not in comment_str:
        return comment_str
    
    try:
        comment_data = json.loads(comment_str)
        if isinstance(comment_data, dict) and 'lines' in comment_data:
            lines = comment_data.get('lines', [])
            if isinstance(lines, list):
                result = {}
                for i, line in enumerate(lines):
                    # 提取冒号或：之后的部分作为值
                    if ':' in line or '：' in line:
                        # 替换中文冒号为英文冒号
                        line = line.replace('：', ':')
                        # 分割键和值
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            key = parts[0].strip()
                            value = parts[1].strip()
                            result[key] = value
                    elif ';' in line:
                        # 处理分号的情况
                        parts = line.split(';', 1)
                        if len(parts) == 2:
                            key = parts[0].strip()
                            value = parts[1].strip()
                            result[key] = value
                
                if result:
                    return json.dumps(result, ensure_ascii=False)
    except (json.JSONDecodeError, ValueError):
        pass
    
    return comment_str


def convert_csv(input_file, output_file, encoding='gb2312'):
    """转换 CSV 文件中的 comment 格式"""
    try:
        # 读取 CSV
        rows = []
        with open(input_file, 'r', encoding=encoding) as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for row in reader:
                # 转换备注(JSON)列
                if '备注(JSON)' in row and row['备注(JSON)']:
                    row['备注(JSON)'] = convert_lines_to_dict(row['备注(JSON)'])
                rows.append(row)
        
        # 写入 CSV
        with open(output_file, 'w', encoding=encoding, newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        print(f"✓ 转换完成: {output_file}")
        return True
        
    except Exception as e:
        print(f"✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    input_csv = 'outputs/LvKong_1C_V2.5_A484_A485_100_00B_unified.csv'
    output_csv = 'outputs/LvKong_1C_V2.5_A484_A485_100_00B_unified_converted.csv'
    
    if convert_csv(input_csv, output_csv):
        # 验证转换
        print("\n验证转换结果:")
        with open(output_csv, 'r', encoding='gb2312') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                comment = row.get('备注(JSON)', '')
                if comment and ('lines' not in comment or '00:' in comment or '01' in comment):
                    if 'lines' not in comment and comment.startswith('{'):
                        count += 1
                        if count <= 5:  # 只打印前 5 条
                            signal_name = row.get('信号名称', '')
                            print(f"  {signal_name}: {comment}")
        print(f"\n共发现并转换了包含 'lines' 的注释")
