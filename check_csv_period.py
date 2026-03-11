import csv

with open('outputs/LvKong_1C_V2.5_A484_A485_100_00B_unified.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    
    # 用来追踪已处理过的消息
    processed_msgs = set()
    
    print('CSV 中的周期信息（来自消息备注列）：')
    print('='*60)
    
    for row in reader:
        msg_name = row['消息名称']
        if msg_name not in processed_msgs:
            processed_msgs.add(msg_name)
            comment = row['消息备注(JSON)']
            print(f'{msg_name}: {comment if comment else "(空)"}')
