import pandas as pd
import json

# 读取CSV
csv_path = 'outputs/GTAKE_motor_unified.csv'
df = pd.read_csv(csv_path, encoding='utf-8')

# 分析接收消息（发送者为HCU）
rx_msgs = df[df['发送者'] == 'HCU']
print('=== 接收消息分析 ===')
print('消息ID:', rx_msgs['消息ID'].unique()[0] if len(rx_msgs) > 0 else 'N/A')
print('消息名称:', rx_msgs['消息名称'].unique()[0] if len(rx_msgs) > 0 else 'N/A')
print('信号数量:', len(rx_msgs))

print('\n=== 信号详情 ===')
for idx, row in rx_msgs.iterrows():
    备注 = row.get('备注(JSON)', '')
    print(f"{row['信号名称']:30s} 起始位:{row['起始位']:3d} 长度:{row['长度(bit)']:2d}bit 缩放:{row['缩放系数']} 偏移:{row['偏移']} 备注:{备注}")

# 生成配置
config = {
    "msg_id": "0x0CFF05EF",
    "msg_struct": "g_SaeRxMsg[0].Data.MotRx1",
    
    "mapping_analysis": {
        "description": "GTAKE电机控制协议映射分析",
        "rx_message": "TM_HCU_Command",
        "total_signals_in_protocol": 10,
        "signals_used_in_function": 10,
        "signals_missing": 0
    },
    
    # 纯数值信号 [信号名, 起始位, 长度, 缩放, 偏移, 输出变量]
    "numbers": [
        {"signal_name": "TM_Demand_Torque", "start_bit": 32, "length": 16, "scale": 1, "offset": -5000, "output_var": "RefTempTorq"},
        {"signal_name": "TM_Demand_Speed", "start_bit": 48, "length": 16, "scale": 1, "offset": -15000, "output_var": "RxSpdRefValue"},
        {"signal_name": "TM_Demand_Limit_High", "start_bit": 8, "length": 12, "scale": 4, "offset": 0, "output_var": "RxFwdSpdLimValue"},
        {"signal_name": "TM_Demand_Limit_Low", "start_bit": 20, "length": 12, "scale": 4, "offset": 0, "output_var": "RxRevSpdLimValue"}
    ],
    
    # 开关量/枚举信号 [信号名, 输出字段, 逻辑类型, 参数]
    "switches": [
        {"signal_name": "TM_MCU_Enable", "output_field": "RunOrStop", "logic_type": "simple", "params": ""},
        {"signal_name": "TM_Fault_Reset", "output_field": "FaultReset", "logic_type": "simple", "params": ""},
        {"signal_name": "TM_Control_Mode", "output_field": "SpdTorqModSel", "logic_type": "cond", "params": "1:1,2:0,3:0,*:0"},
        {"signal_name": "TM_Gear", "output_field": "Direction", "logic_type": "complex", "params": "gear"},
        {"signal_name": "TM_FootBrake", "output_field": "Braking", "logic_type": "or", "params": "TM_HandBrake"}
    ],
    
    "has_gear": True,
    "has_active_discharge": True,
    "active_discharge_signal": "TM_Control_Mode",
    "active_discharge_value": 3,
    
    # 缺失信号
    "missing": [
        {
            "output_var": "RxDrvTorLimValue",
            "searched_signals": ["驱动转矩限制", "Drive Torque Limit"],
            "found": False,
            "action": "default_zero"
        },
        {
            "output_var": "RxBrkTorLimValue",
            "searched_signals": ["制动转矩限制", "Brake Torque Limit"],
            "found": False,
            "action": "default_zero"
        }
    ]
}

# 保存配置
with open('outputs/config.json', 'w', encoding='utf-8') as f:
    json.dump(config, f, indent=2, ensure_ascii=False)

print('\n=== 配置已生成 ===')
print('文件路径: outputs/config.json')
