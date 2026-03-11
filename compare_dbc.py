#!/usr/bin/env python
"""详细对比两个 DBC 文件并输出差异"""

import cantools
import sys

def compare_signals(sig1, sig2, msg_name):
    """对比两个信号"""
    differences = []
    
    attrs = ['start', 'length', 'is_signed', 'byte_order', 'scale', 'offset', 
             'minimum', 'maximum', 'unit', 'receivers', 'comment']
    
    for attr in attrs:
        val1 = getattr(sig1, attr, None)
        val2 = getattr(sig2, attr, None)
        
        if val1 != val2:
            differences.append(f"  {attr}: {val1} -> {val2}")
    
    return differences

def compare_dbc_detailed(dbc1_path, dbc2_path):
    """详细对比两个 DBC 文件"""
    
    print(f"加载文件 1: {dbc1_path}")
    db1 = cantools.database.load_file(dbc1_path, encoding='gb2312')
    
    print(f"加载文件 2: {dbc2_path}")
    db2 = cantools.database.load_file(dbc2_path, encoding='gb2312')
    
    print("\n" + "="*60)
    print("DBC 文件对比结果")
    print("="*60)
    
    print(f"\n消息数: {len(db1.messages)} vs {len(db2.messages)}")
    print(f"信号数: {sum(len(m.signals) for m in db1.messages)} vs {sum(len(m.signals) for m in db2.messages)}")
    
    has_differences = False
    
    # 对比消息
    for msg1 in db1.messages:
        try:
            msg2 = db2.get_message_by_name(msg1.name)
        except KeyError:
            print(f"\n✗ 消息 '{msg1.name}' 在文件 2 中不存在")
            has_differences = True
            continue
        
        # 对比消息属性
        if msg1.frame_id != msg2.frame_id:
            print(f"\n✗ 消息 '{msg1.name}' ID 不匹配: {msg1.frame_id} vs {msg2.frame_id}")
            has_differences = True
        
        if msg1.length != msg2.length:
            print(f"\n✗ 消息 '{msg1.name}' 长度不匹配: {msg1.length} vs {msg2.length}")
            has_differences = True
        
        if msg1.is_extended_frame != msg2.is_extended_frame:
            print(f"\n✗ 消息 '{msg1.name}' 扩展帧标志不匹配: {msg1.is_extended_frame} vs {msg2.is_extended_frame}")
            has_differences = True
        
        if msg1.comment != msg2.comment:
            print(f"\n⚠ 消息 '{msg1.name}' 注释不匹配:")
            print(f"  原始: {msg1.comment}")
            print(f"  生成: {msg2.comment}")
        
        # 对比信号
        if len(msg1.signals) != len(msg2.signals):
            print(f"\n✗ 消息 '{msg1.name}' 信号数不匹配: {len(msg1.signals)} vs {len(msg2.signals)}")
            has_differences = True
        
        for sig1 in msg1.signals:
            try:
                sig2 = msg2.get_signal_by_name(sig1.name)
            except KeyError:
                print(f"\n✗ 信号 '{sig1.name}' 在消息 '{msg1.name}' 中不存在")
                has_differences = True
                continue
            
            diffs = compare_signals(sig1, sig2, msg1.name)
            if diffs:
                print(f"\n⚠ 信号 '{msg1.name}.{sig1.name}' 有差异:")
                for diff in diffs:
                    print(diff)
                has_differences = True
    
    print("\n" + "="*60)
    if not has_differences:
        print("✓ 两个文件完全一致!")
        return True
    else:
        print("✗ 存在差异，需要修复")
        return False
    print("="*60)


if __name__ == '__main__':
    dbc1 = 'LvKong_1C_V2.5_A484_A485_100_00B.dbc'
    dbc2 = 'outputs/LvKong_1C_V2.5_A484_A485_100_00B_from_unified.dbc'
    
    success = compare_dbc_detailed(dbc1, dbc2)
    sys.exit(0 if success else 1)
