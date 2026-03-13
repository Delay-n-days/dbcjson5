//*********************************** 宏定义 *********************************************//
//*********************************** CAN通讯接收数据帧个数 *********************************************//
#define SAE_MAX_RX_NUM  		1

//*********************************** CAN通讯发送数据帧个数 *******************************************//
#define SAE_MAX_TX_NUM  		4	//注意此处为协议定义发送个数,不用预留

//*********************************** CAN通讯数据帧格式 *********************************************//
#define EXIDEEN   				1   // 0:无效 1:使能扩展帧
#define STDIDEEN   				0   // 0:无效 1:使能标准帧

//*********************************** CAN通讯波特率设置 ***********************************************//
#define BAUD250					1   // 0:无效 1:250K波特率
#define BAUD500					0   // 0:无效 1:500K波特率

//******************************CAN通讯接收帧ID*******************************************//
#define CAN_ID_EVCU1 			((unsigned long)0x0CFF08EF)	// 接收VCU帧ID,ID=0x0CFF08EF

//*************************** CAN通讯发送数据帧周期(单位ms)*******************************//
#define MCUMSGTX0TIME			10	//报文发送周期
#define MCUMSGTX1TIME			50	//报文发送周期
#define MCUMSGTX2TIME			100	//报文发送周期
#define MCUMSGTX3TIME			100	//报文发送周期

//*************************** CAN通讯数据帧结构体定义 ************************************//
// 接收报文1 :ISG_HCU_Command
typedef struct __MOT_RX_APP1       
{
    // Byte0 ---------------------------------------------------
    unsigned MCU_Enable       : 1; // 0:disable; 1:enable 
    unsigned FaultReset       : 1; // 0:disable; 1:enable 
    unsigned CtrlMode         : 2; // 0:Reserved; 1:Speed Control; 2:Torque Control; 3:Active Discharge 
    unsigned LiveCounter      : 4; // 循环计数器Alive Rolling Counter 
    // Byte1 ---------------------------------------------------
    unsigned DemandLimitHigh_L: 8; // 转矩转速指令限值上限转矩控制模式时转速限制起作用转速控制模式时转矩限制起作用转矩单位Nm转速单位rpm缩放系数转矩1转速4 
    // Byte2 ---------------------------------------------------
    unsigned DemandLimitHigh_H: 4; // 转矩转速指令限值上限转矩控制模式时转速限制起作用转速控制模式时转矩限制起作用转矩单位Nm转速单位rpm缩放系数转矩1转速4 
    unsigned DemandLimitLow_L : 4; // 转矩转速指令限值下限网络上发送的是正数值但电机控制器实际执行按负值处理 
    // Byte3 ---------------------------------------------------
    unsigned DemandLimitLow_H : 8; // 转矩转速指令限值下限网络上发送的是正数值但电机控制器实际执行按负值处理 
    // Byte4 ---------------------------------------------------
    unsigned DemandTorque_L   : 8; // 转矩的正负表示力的方向规定发动机旋转方向为正向 
    // Byte5 ---------------------------------------------------
    unsigned DemandTorque_H   : 8; // 转矩的正负表示力的方向规定发动机旋转方向为正向 
    // Byte6 ---------------------------------------------------
    unsigned DemandSpeed_L    : 8; // 转速的正负表示电机旋转的方向与发动机正常转动方向同向为正  
    // Byte7 ---------------------------------------------------
    unsigned DemandSpeed_H    : 8; // 转速的正负表示电机旋转的方向与发动机正常转动方向同向为正  


}TYPE_MOT_RX_APP1;

// 发送报文1：ISG_MCU_Status1
// ID = 0x0CFF0008
// T=10ms
typedef struct __MOTOR_TX1
{
    // Byte0 ---------------------------------------------------
    unsigned MotorSpeed_L       : 8; // 电机转速正负表示电机转向转速为正时与发动机正常转动方向一致 
    // Byte1 ---------------------------------------------------
    unsigned MotorSpeed_H       : 8; // 电机转速正负表示电机转向转速为正时与发动机正常转动方向一致 
    // Byte2 ---------------------------------------------------
    unsigned MotorTorque_L      : 8; // 扭矩大于0为转矩方向与发动机转向相同 
    // Byte3 ---------------------------------------------------
    unsigned MotorTorque_H      : 8; // 扭矩大于0为转矩方向与发动机转向相同 
    // Byte4 ---------------------------------------------------
    unsigned MotorACCurrent_L   : 8; // 交流侧电流有效值反馈AC Current RMS value feedback 
    // Byte5 ---------------------------------------------------
    unsigned MotorACCurrent_H   : 8; // 交流侧电流有效值反馈AC Current RMS value feedback 
    // Byte6 ---------------------------------------------------
    unsigned Res1               : 4; // 预留 
    unsigned PrechargeAllow     : 1; // 0:disable; 1:enable 
    unsigned ActDischgEnableFdbk: 1; // 0:disable; 1:enable 
    unsigned IGBTEnableFeedback : 1; // 0:disable; 1:enable 
    unsigned Res2               : 1; // 预留 
    // Byte7 ---------------------------------------------------
    unsigned Res3               : 4; // 预留 
    unsigned LiveCounter        : 4; // 循环计数器Alive Rolling Counter  
}TYPE_MOT_TX1;


// 发送报文2：ISG_MCU_Status2
// ID = 0x0CFF0108
// T=50ms
typedef struct __MOTOR_TX2
{
    // Byte0 ---------------------------------------------------
    unsigned MotorTemperature : 8; // 电机本体温度最低温只能测到22度 
    // Byte1 ---------------------------------------------------
    unsigned MCUTemperature   : 8; // 电机控制器温度 
    // Byte2 ---------------------------------------------------
    unsigned TorqueLimitHigh_L: 8; // 转矩上限 
    // Byte3 ---------------------------------------------------
    unsigned TorqueLimitHigh_H: 8; // 转矩上限 
    // Byte4 ---------------------------------------------------
    unsigned TorqueLimitLow_L : 8; // 转矩下限 
    // Byte5 ---------------------------------------------------
    unsigned TorqueLimitLow_H : 8; // 转矩下限 
    // Byte6 ---------------------------------------------------
    unsigned FailGrade        : 4; // 0:No Fault; 1:Warning(degraded); 2:Fault(zero torque output); 3:Fault(shut down MCU); 4:Serious Fault(need to stop the vehicle) 
    unsigned Res1             : 4; // 预留 
    // Byte7 ---------------------------------------------------
    unsigned Res2             : 4; // 预留 
    unsigned LiveCounter      : 4; // 循环计数器Alive Rolling Counter  
}TYPE_MOT_TX2;


// 发送报文3：ISG_MCU_Status3
// ID = 0x0CFF0208
// T=100ms
typedef struct __MOTOR_TX3
{
    // Byte0 ---------------------------------------------------
    unsigned DTCCode_L       : 8; // 错误故障码Diagnostic Trouble Code 
    // Byte1 ---------------------------------------------------
    unsigned DTCCode_H       : 8; // 错误故障码Diagnostic Trouble Code 
    // Byte2 ---------------------------------------------------
    unsigned DCCurrent_L     : 8; // 直流电流估计值不建议作为控制量电机驱动状态为负发电状态为正 
    // Byte3 ---------------------------------------------------
    unsigned DCCurrent_H     : 8; // 直流电流估计值不建议作为控制量电机驱动状态为负发电状态为正 
    // Byte4 ---------------------------------------------------
    unsigned DCVoltage_L     : 8; // 直流电压 
    // Byte5 ---------------------------------------------------
    unsigned DCVoltage_H     : 8; // 直流电压 
    // Byte6 ---------------------------------------------------
    unsigned MotorRotationCnt: 8; // 电机转数循环计数到255后回0用于记录转了多少圈满255之后清零可以和仪表配合进行精确里程计算 
    // Byte7 ---------------------------------------------------
    unsigned Res1            : 4; // 预留 
    unsigned LiveCounter     : 4; // 循环计数器Alive Rolling Counter  
}TYPE_MOT_TX3;


// 发送报文4：ISG_MCU_Status4
// ID = 0x0CFF0308
// T=100ms
typedef struct __MOTOR_TX4
{
    // Byte0 ---------------------------------------------------
    unsigned HwErrCode1 : 8; // 1:母线电压欠压故障; 2:母线电压过压故障 
    // Byte1 ---------------------------------------------------
    unsigned HwErrCode2 : 8; // 1:硬件限流故障; 2:硬件过流故障 
    // Byte2 ---------------------------------------------------
    unsigned HwErrCode3 : 8; // 1:电机控制器温度断线故障; 2:电机控制器过温故障; 3:电机温度断线故障; 4:电机温度过温故障 
    // Byte3 ---------------------------------------------------
    unsigned HwErrCode4 : 8; // 1:IGBT模块故障 
    // Byte4 ---------------------------------------------------
    unsigned HwErrCode5 : 8; // 1:编码器断线故障 
    // Byte5 ---------------------------------------------------
    unsigned HwErrCode6 : 8; // 1:控制器内部控制电源异常故障5V异常; 2:外供控制器控制电源异常故障24V输入断线或低于18V 
    // Byte6 ---------------------------------------------------
    unsigned Res1       : 8; // 预留 
    // Byte7 ---------------------------------------------------
    unsigned Res2       : 4; // 预留 
    unsigned LiveCounter: 4; // 循环计数器Alive Rolling Counter  
}TYPE_MOT_TX4;


typedef union __SAE_DATA
{
	unsigned int WordArray[4];
	SAE_Bytes Bytes;
	TYPE_MOT_RX_APP1 MotRx1;  // ISG_HCU_Command 
	TYPE_MOT_TX1 MotTx1; // ISG_MCU_Status1
	TYPE_MOT_TX2 MotTx2; // ISG_MCU_Status2
	TYPE_MOT_TX3 MotTx3; // ISG_MCU_Status3
	TYPE_MOT_TX4 MotTx4; // ISG_MCU_Status4
}SAE_DATA;
