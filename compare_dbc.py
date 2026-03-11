#!/usr/bin/env python
"""对比两个 DBC 文件的一致性"""

import cantools
from pathlib import Path

def compare_signals(sig1, sig2, msg_name):
    """对比两个信号是否相同"""
    issues = []
    
    if sig1.name != sig2.name:
        issues.append(f"  ✗ 信号名称不匹配: {sig1.name} vs {sig2.name}")
    if sig1.start != sig2.start:
        issues.append(f"  ✗ {sig1.name} 起始位不匹配: {sig1.start} vs {sig2.start}")
    if sig1.length != sig2.length:
        issues.append(f"  ✗ {sig1.name} 长度不匹配: {sig1.length} vs {sig2.length}")
    if sig1.byte_order != sig2.byte_order:
        issues.append(f"  ✗ {sig1.name} 字节序不匹配: {sig1.byte_order} vs {sig2.byte_order}")
    if sig1.is_signed != sig2.is_signed:
        issues.append(f"  ✗ {sig1.name} 有符号标志不匹配: {sig1.is_signed} vs {sig2.is_signed}")
    
    # 对比注释
    comment1 = sig1.comment or ''
    comment2 = sig2.comment or ''
    if comment1 != comment2:
        issues.append(f"  ⚠ {sig1.name} 注释不匹配:")
        issues.append(f"    生成: {repr(comment1)}")
        issues.append(f"    预期: {repr(comment2)}")
    
    return issues


def compare_messages(msg1, msg2):
    """对比两个消息是否相同"""
    issues = []
    
    if msg1.frame_id != msg2.frame_id:
        issues.append(f"✗ 消息 {msg1.name} ID 不匹配: {msg1.frame_id} vs {msg2.frame_id}")
    if msg1.length != msg2.length:
        issues.append(f"✗ 消息 {msg1.name} 长度不匹配: {msg1.length} vs {msg2.length}")
    if len(msg1.signals) != len(msg2.signals):
        issues.append(f"✗ 消息 {msg1.name} 信号数不匹配: {len(msg1.signals)} vs {len(msg2.signals)}")
    
    # 对比消息注释
    msg_comment1 = msg1.comment or ''
    msg_comment2 = msg2.comment or ''
    if msg_comment1 != msg_comment2:
        issues.append(f"⚠ 消息 {msg1.name} 注释不匹配:")
        issues.append(f"  生成: {repr(msg_comment1)}")
        issues.append(f"  预期: {repr(msg_comment2)}")
    
    # 对比信号
    signals1 = {sig.name: sig for sig in msg1.signals}
    signals2 = {sig.name: sig for sig in msg2.signals}
    
    for sig_name in signals1:
        if sig_name in signals2:
            sig_issues = compare_signals(signals1[sig_name], signals2[sig_name], msg1.name)
            issues.extend(sig_issues)
        else:
            issues.append(f"  ✗ 信号 {sig_name} 在预期 DBC 中不存在")
    
    for sig_name in signals2:
        if sig_name not in signals1:
            issues.append(f"  ✗ 信号 {sig_name} 在生成 DBC 中不存在")
    
    return issues


def compare_dbc_files(generated_dbc, expected_dbc):
    """对比两个 DBC 文件"""
    print(f"对比 DBC 文件:")
    print(f"  生成文件: {generated_dbc}")
    print(f"  预期文件: {expected_dbc}")
    print()
    
    try:
        db_generated = cantools.database.load_file(generated_dbc, encoding='gb2312')
        db_expected = cantools.database.load_file(expected_dbc, encoding='gb2312')
    except Exception as e:
        print(f"✗ 加载 DBC 文件失败: {e}")
        return False
    
    issues = []
    
    # 对比消息数量
    if len(db_generated.messages) != len(db_expected.messages):
        issues.append(f"✗ 消息数不匹配: {len(db_generated.messages)} vs {len(db_expected.messages)}")
    
    # 对比每条消息
    messages_generated = {msg.name: msg for msg in db_generated.messages}
    messages_expected = {msg.name: msg for msg in db_expected.messages}
    
    all_msg_names = set(messages_generated.keys()) | set(messages_expected.keys())
    
    for msg_name in sorted(all_msg_names):
        if msg_name in messages_generated and msg_name in messages_expected:
            msg_issues = compare_messages(messages_generated[msg_name], messages_expected[msg_name])
            if msg_issues:
                issues.append(f"\n消息 '{msg_name}':")
                issues.extend(msg_issues)
        elif msg_name not in messages_generated:
            issues.append(f"\n✗ 消息 '{msg_name}' 在生成 DBC 中不存在")
        else:
            issues.append(f"\n✗ 消息 '{msg_name}' 在预期 DBC 中不存在")
    
    # 输出结果
    if issues:
        print("发现以下差异:")
        for issue in issues:
            print(issue)
        print(f"\n✗ 对比失败，共发现 {len(issues)} 项差异")
        return False
    else:
        print("✓ 两个 DBC 文件完全一致！")
        return True


if __name__ == '__main__':
    generated_dbc = 'outputs/LvKong_1C_V2.5_A484_A485_100_00B_from_unified.dbc'
    expected_dbc = 'LvKong_1C_V2.5_A484_A485_100_00B.dbc'
    
    if not Path(generated_dbc).exists():
        print(f"✗ 生成的 DBC 文件不存在: {generated_dbc}")
        exit(1)
    
    if not Path(expected_dbc).exists():
        print(f"✗ 预期 DBC 文件不存在: {expected_dbc}")
        exit(1)
    
    success = compare_dbc_files(generated_dbc, expected_dbc)
    exit(0 if success else 1)
