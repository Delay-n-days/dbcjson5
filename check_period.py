import cantools

db = cantools.database.load_file('LvKong_1C_V2.5_A484_A485_100_00B.dbc', encoding='gb2312')

print('原始 DBC 中的周期信息：')
print('='*60)
for msg in db.messages:
    period = f"{msg.cycle_time}ms" if msg.cycle_time else "未定义"
    print(f"{msg.name}: {period}")
