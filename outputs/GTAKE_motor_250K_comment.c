// TM_MCU_Enable	起始位:0	长度:1	系数:1	偏移量:0	0:disable	
// 1:enable

// TM_Fault_Reset	起始位:1	长度:1	系数:1	偏移量:0	0:disable	
// 1:enable

// TM_Control_Mode	起始位:2	长度:2	系数:1	偏移量:0	0:Reserved	
// 1:Speed Control	
// 2 = Torque Control	
// 3 = Active Discharge

// TM_Gear	起始位:4	长度:2	系数:1	偏移量:0	0:Neutral	
// 1:Drive	
// 2 = Reverse

// TM_FootBrake	起始位:6	长度:1	系数:1	偏移量:0	0:No FootBrake	
// 1:FootBrake

// TM_HandBrake	起始位:7	长度:1	系数:1	偏移量:0	0:No HandBrake	
// 1:HandBrake

// TM_Demand_Limit_High	起始位:8	长度:12	系数:4	偏移量:0	单位:rpm	转速指令限值上限，转矩控制模式时起作用

// TM_Demand_Limit_Low	起始位:20	长度:12	系数:4	偏移量:0	单位:rpm	转速指令限值下限，转矩控制模式时起作用，网络发送正值但电机控制器按负值处理

// TM_Demand_Torque	起始位:32	长度:16	系数:1	偏移量:-5000	单位:Nm	转矩的正负表示力的方向，发动机旋转方向为正向

// TM_Demand_Speed	起始位:48	长度:16	系数:1	偏移量:-15000	单位:rpm	转速的正负表示电机旋转的方向，与发动机正常转动方向同向为正

// TM_Motor_Speed	起始位:0	长度:16	系数:1	偏移量:-15000	单位:rpm	电机转速正负表示电机转向，转速为正时与发动机正常转动方向一致

// TM_Motor_Torque	起始位:16	长度:16	系数:1	偏移量:-5000	单位:Nm	扭矩大于0为转矩方向与发动机转向相同

// TM_Motor_AC_Current	起始位:32	长度:16	系数:0.1	偏移量:0	单位:A	交流侧电流有效值反馈

// TM_Precharge_Allow	起始位:52	长度:1	系数:1	偏移量:0	0:disable	
// 1:enable

// TM_Active_Discharge_Enable	起始位:53	长度:1	系数:1	偏移量:0	0:disable	
// 1:enable

// TM_IGBT_Enable_Feedback	起始位:54	长度:1	系数:1	偏移量:0	0:disable	
// 1:enable

// TM_Life_Counter_1	起始位:60	长度:4	系数:1	偏移量:0	循环计数器

// TM_Motor_Temperature	起始位:0	长度:8	系数:1	偏移量:-40	单位:℃	电机温度

// TM_MCU_Temperature	起始位:8	长度:8	系数:1	偏移量:-40	单位:℃	电机控制器温度

// TM_Torque_Limit_High	起始位:16	长度:16	系数:1	偏移量:0	单位:Nm	转矩上限

// TM_Torque_Limit_Low	起始位:32	长度:16	系数:1	偏移量:-5000	单位:Nm	转矩下限

// TM_Fail_Grade	起始位:48	长度:4	系数:1	偏移量:0	0:No Fault	
// 1:Warning(degraded)	
// 2 = Fault(zero torque output)	
// 3 = Fault(shut down MCU)

// TM_Life_Counter_2	起始位:60	长度:4	系数:1	偏移量:0	循环计数器

// TM_Fault_Code	起始位:0	长度:8	系数:1	偏移量:0	错误故障码

// TM_Alarm_Code	起始位:8	长度:8	系数:1	偏移量:0	告警故障码

// TM_DC_Current	起始位:16	长度:16	系数:1	偏移量:-1000	单位:A	直流电流（估计值，不建议作为控制量），电机驱动状态为负，发电状态为正

// TM_DC_Voltage	起始位:32	长度:16	系数:0.1	偏移量:0	单位:V	直流电压

// TM_Life_Counter_3	起始位:48	长度:4	系数:1	偏移量:0	循环计数器
