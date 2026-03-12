//*********************************** 宏定义 *********************************************//
//*********************************** CAN通讯接收数据帧个数 *********************************************//
#define SAE_MAX_RX_NUM  		1

//*********************************** CAN通讯发送数据帧个数 *******************************************//
#define SAE_MAX_TX_NUM  		3	//注意此处为协议定义发送个数,不用预留

//*********************************** CAN通讯数据帧格式 *********************************************//
#define EXIDEEN   				1   // 0:无效 1:使能扩展帧
#define STDIDEEN   				0   // 0:无效 1:使能标准帧

//*********************************** CAN通讯波特率设置 ***********************************************//
#define BAUD250					1   // 0:无效 1:250K波特率
#define BAUD500					0   // 0:无效 1:500K波特率

//******************************CAN通讯接收帧ID*******************************************//
#define CAN_ID_EVCU1 			((unsigned long)0x0CFF05EF)	// 接收VCU帧ID,ID=0x0CFF08EF

//*************************** CAN通讯发送数据帧周期(单位ms)*******************************//
#define MCUMSGTX0TIME			10	//报文发送周期
#define MCUMSGTX1TIME			50 	//报文发送周期
#define MCUMSGTX2TIME			100 //报文发送周期

//*************************** CAN通讯数据帧结构体定义 ************************************//
// 接收报文1 :TM_HCU_Command
typedef struct __MOT_RX_APP1       
{
    // Byte0 ---------------------------------------------------
    unsigned TM_MCU_Enable         : 1; // 0:disable; 1:enable 
    unsigned TM_Fault_Reset        : 1; // 0:disable; 1:enable 
    unsigned TM_Control_Mode       : 2; // 0:Reserved; 1:Speed Control; 2 = Torque Control; 3 = Active Discharge 
    unsigned TM_Gear               : 2; // 0:Neutral; 1:Drive; 2 = Reverse 
    unsigned TM_FootBrake          : 1; // 0:No FootBrake; 1:FootBrake 
    unsigned TM_HandBrake          : 1; // 0:No HandBrake; 1:HandBrake 
    // Byte1 ---------------------------------------------------
    unsigned TM_Demand_Limit_High_L: 8; // 转速指令限值上限，转矩控制模式时起作用 
    // Byte2 ---------------------------------------------------
    unsigned TM_Demand_Limit_High_H: 4; // 转速指令限值上限，转矩控制模式时起作用 
    unsigned TM_Demand_Limit_Low_L : 4; // 转速指令限值下限，转矩控制模式时起作用，网络发送正值但电机控制器按负值处理 
    // Byte3 ---------------------------------------------------
    unsigned TM_Demand_Limit_Low_H : 8; // 转速指令限值下限，转矩控制模式时起作用，网络发送正值但电机控制器按负值处理 
    // Byte4 ---------------------------------------------------
    unsigned TM_Demand_Torque_L    : 8; // 转矩的正负表示力的方向，发动机旋转方向为正向 
    // Byte5 ---------------------------------------------------
    unsigned TM_Demand_Torque_H    : 8; // 转矩的正负表示力的方向，发动机旋转方向为正向 
    // Byte6 ---------------------------------------------------
    unsigned TM_Demand_Speed_L     : 8; // 转速的正负表示电机旋转的方向，与发动机正常转动方向同向为正  
    // Byte7 ---------------------------------------------------
    unsigned TM_Demand_Speed_H     : 8; // 转速的正负表示电机旋转的方向，与发动机正常转动方向同向为正  


}TYPE_MOT_RX_APP1;

// 发送报文1：TM_MCU_STATUS_1
// ID = 0x0CFF0005
// T=10ms
typedef struct __MOTOR_TX1
{
    // Byte0 ---------------------------------------------------
    unsigned TM_Motor_Speed_L          : 8; // 电机转速正负表示电机转向，转速为正时与发动机正常转动方向一致 
    // Byte1 ---------------------------------------------------
    unsigned TM_Motor_Speed_H          : 8; // 电机转速正负表示电机转向，转速为正时与发动机正常转动方向一致 
    // Byte2 ---------------------------------------------------
    unsigned TM_Motor_Torque_L         : 8; // 扭矩大于0为转矩方向与发动机转向相同 
    // Byte3 ---------------------------------------------------
    unsigned TM_Motor_Torque_H         : 8; // 扭矩大于0为转矩方向与发动机转向相同 
    // Byte4 ---------------------------------------------------
    unsigned TM_Motor_AC_Current_L     : 8; // 交流侧电流有效值反馈 
    // Byte5 ---------------------------------------------------
    unsigned TM_Motor_AC_Current_H     : 8; // 交流侧电流有效值反馈 
    // Byte6 ---------------------------------------------------
    unsigned Res1                      : 4; // 预留 
    unsigned TM_Precharge_Allow        : 1; // 0:disable; 1:enable 
    unsigned TM_Active_Discharge_Enable: 1; // 0:disable; 1:enable 
    unsigned TM_IGBT_Enable_Feedback   : 1; // 0:disable; 1:enable 
    unsigned Res2                      : 1; // 预留 
    // Byte7 ---------------------------------------------------
    unsigned Res3                      : 4; // 预留 
    unsigned TM_Life_Counter_1         : 4; // 循环计数器  
}TYPE_MOT_TX1;

// 发送报文2：TM_MCU_STATUS_2
// ID = 0x0CFF0105
// T=50ms
typedef struct __MOTOR_TX2
{
    // Byte0 ---------------------------------------------------
    unsigned TM_Motor_Temperature  : 8; // 电机温度 
    // Byte1 ---------------------------------------------------
    unsigned TM_MCU_Temperature    : 8; // 电机控制器温度 
    // Byte2 ---------------------------------------------------
    unsigned TM_Torque_Limit_High_L: 8; // 转矩上限 
    // Byte3 ---------------------------------------------------
    unsigned TM_Torque_Limit_High_H: 8; // 转矩上限 
    // Byte4 ---------------------------------------------------
    unsigned TM_Torque_Limit_Low_L : 8; // 转矩下限 
    // Byte5 ---------------------------------------------------
    unsigned TM_Torque_Limit_Low_H : 8; // 转矩下限 
    // Byte6 ---------------------------------------------------
    unsigned TM_Fail_Grade         : 4; // 0:No Fault; 1:Warning(degraded); 2 = Fault(zero torque output); 3 = Fault(shut down MCU) 
    unsigned Res1                  : 4; // 预留 
    // Byte7 ---------------------------------------------------
    unsigned Res2                  : 4; // 预留 
    unsigned TM_Life_Counter_2     : 4; // 循环计数器  
}TYPE_MOT_TX2;


// 发送报文3：TM_MCU_STATUS_3
// ID = 0x0CFF0205
// T=100ms
typedef struct __MOTOR_TX3
{
    // Byte0 ---------------------------------------------------
    unsigned TM_Motor_Temperature: 8; // 电机温度TM_Fault_Code 0 8  
    // Byte1 ---------------------------------------------------
    unsigned TM_Alarm_Code       : 8; // 告警故障码 
    // Byte2 ---------------------------------------------------
    unsigned TM_DC_Current_L     : 8; // 直流电流（估计值，不建议作为控制量），电机驱动状态为负，发电状态为正 
    // Byte3 ---------------------------------------------------
    unsigned TM_DC_Current_H     : 8; // 直流电流（估计值，不建议作为控制量），电机驱动状态为负，发电状态为正 
    // Byte4 ---------------------------------------------------
    unsigned TM_DC_Voltage_L     : 8; // 直流电压 
    // Byte5 ---------------------------------------------------
    unsigned TM_DC_Voltage_H     : 8; // 直流电压 
    // Byte6 ---------------------------------------------------
    unsigned TM_Life_Counter_3   : 4; // 循环计数器 
    unsigned Res1                : 4; // 预留 
    // Byte7 ---------------------------------------------------
    unsigned Res2                : 8; // 预留  
}TYPE_MOT_TX3;

typedef union __SAE_DATA
{
	unsigned int WordArray[4];
	SAE_Bytes Bytes;
	TYPE_MOT_RX_APP1 MotRx1;  // TM_HCU_Command 
	TYPE_MOT_TX1 MotTx1; // TM_MCU_STATUS_1
	TYPE_MOT_TX2 MotTx2; // TM_MCU_STATUS_2
	TYPE_MOT_TX3 MotTx3; // TM_MCU_STATUS_3
}SAE_DATA;
