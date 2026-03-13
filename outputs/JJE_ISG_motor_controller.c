/* =============================================== */
/参考模板，严格遵循原始代码格式
/* =============================================== */

//* ****  部分代码段  ****  *

		// 局部变量声明
		long RefTempTorq = 0;  // 扭矩给定（临时变量）

		//RefTempTorq(单位NM)
		// DemandTorque	起始位:32	长度:16	系数:1.0	偏移量:-5000.0	单位:Nm	转矩的正负表示力的方向规定发动机旋转方向为正向
		raw = ((Uint16)g_SaeRxMsg[0].Data.MotRx1.DemandTorque_L & 0x00FF) | ((Uint16)g_SaeRxMsg[0].Data.MotRx1.DemandTorque_H << 8);
		RefTempTorq = SignalDecode(raw, IN_RATIO(1), OUT_RATIO(1), -5000L);

		//RxDrvTorLimValue(单位NM)
		lngTemp1 = 0;  // DBC 未提及，默认赋值为0
		RxDrvTorLimValue = lngTemp1;

		//RxBrkTorLimValue(单位NM)
		lngTemp1 = 0;  // DBC 未提及，默认赋值为0
		RxBrkTorLimValue = lngTemp1;

		//RxSpdRefValue(单位NM)
		// DemandSpeed	起始位:48	长度:16	系数:1.0	偏移量:-15000.0	单位:rpm	转速的正负表示电机旋转的方向与发动机正常转动方向同向为正
		raw = ((Uint16)g_SaeRxMsg[0].Data.MotRx1.DemandSpeed_L & 0x00FF) | ((Uint16)g_SaeRxMsg[0].Data.MotRx1.DemandSpeed_H << 8);
		RxSpdRefValue = SignalDecode(raw, IN_RATIO(1), OUT_RATIO(1), -15000L);

		//RxFwdSpdLimValue(单位NM)
		// DemandLimitHigh	起始位:8	长度:12	系数:1.0	偏移量:0.0	转矩转速指令限值上限转矩控制模式时转速限制起作用转速控制模式时转矩限制起作用转矩单位Nm转速单位rpm缩放系数转矩1转速4
		raw = ((Uint16)g_SaeRxMsg[0].Data.MotRx1.DemandLimitHigh_L & 0x00FF) | ((Uint16)g_SaeRxMsg[0].Data.MotRx1.DemandLimitHigh_H << 8);
		RxFwdSpdLimValue = SignalDecode(raw, IN_RATIO(1), OUT_RATIO(1), 0L);

		//RxRevSpdLimValue(单位NM)
		// DemandLimitLow	起始位:20	长度:12	系数:1.0	偏移量:0.0	转矩转速指令限值下限网络上发送的是正数值但电机控制器实际执行按负值处理
		raw = ((Uint16)g_SaeRxMsg[0].Data.MotRx1.DemandLimitLow_L & 0x00FF) | ((Uint16)g_SaeRxMsg[0].Data.MotRx1.DemandLimitLow_H << 8);
		RxRevSpdLimValue = SignalDecode(raw, IN_RATIO(1), OUT_RATIO(1), 0L);




		//
		// MCU_Enable	起始位:0	长度:1	系数:1.0	偏移量:0.0	电机控制单元使能控制器的使能指令具体指控制器IGBT的PWM开关指令
		VehicleCmdCanTemp.B.RunOrStop = g_SaeRxMsg[0].Data.MotRx1.MCU_Enable;

		//
		// FaultReset	起始位:1	长度:1	系数:1.0	偏移量:0.0	用于清除控制器的故障主要用于调试整车运行中不建议使用
		VehicleCmdCanTemp.B.FaultReset = g_SaeRxMsg[0].Data.MotRx1.FaultReset;


		//
		// CtrlMode	起始位:2	长度:2	系数:1.0	偏移量:0.0
		if(g_SaeRxMsg[0].Data.MotRx1.CtrlMode == 1)
		{
			VehicleCmdCanTemp.B.SpdTorqModSel = 1;//速度控制
		}
		else if(g_SaeRxMsg[0].Data.MotRx1.CtrlMode == 2)
		{
			VehicleCmdCanTemp.B.SpdTorqModSel = 0;//转矩控制
		}
		else if(g_SaeRxMsg[0].Data.MotRx1.CtrlMode == 3)
		{
			VehicleCmdCanTemp.B.SpdTorqModSel = 0;//转矩控制
		}
		else//其它默认零扭矩控制
		{
			VehicleCmdCanTemp.B.SpdTorqModSel = 0;//转矩控制
			RefTempTorq = 0;
		}

		//
		// CtrlMode	起始位:2	长度:2	系数:1.0	偏移量:0.0
		if(g_SaeRxMsg[0].Data.MotRx1.CtrlMode == 3)
		{
			VehicleCmdCanTemp.B.mainctrl = 1;//速度控制
		}
		else//其它默认零扭矩控制
		{
			VehicleCmdCanTemp.B.mainctrl = 0;//转矩控制
			RefTempTorq = 0;
		}


//*************************************挡位结构体赋值开始******************************************//			
		//有档位软件,特别注意出厂需要将F0-02固化为0x100!!!

	#if 0 //无挡位软件更改为:#if 0

    
		//手刹和脚刹信号有效均将VehicleCmdCanTemp.B.Braking赋为1
		// TM_FootBrake	起始位:6	长度:1	系数:1	偏移量:0	0:No FootBrake;1:FootBrake
		if((g_SaeRxMsg[0].Data.MotRx1.TM_FootBrake == 1)||(g_SaeRxMsg[0].Data.MotRx1.TM_HandBrake == 1))
		{
			VehicleCmdCanTemp.B.Braking = 1;
		}
		else
		{
			VehicleCmdCanTemp.B.Braking = 0;	
		}
		//挡位信号赋值
		// TM_Gear	起始位:4	长度:2	系数:1	偏移量:0	0:Neutral;1:Drive;2:Reverse
		if(g_SaeRxMsg[0].Data.MotRx1.TM_Gear == 1)
		{//D挡
			VehicleCmdCanTemp.B.Direction=1;
			VehicleCmdCanTemp.B.ReDirection = 0;
			VehicleCmdCanTemp.B.NeutralPosition = 0;
		}
		else if(g_SaeRxMsg[0].Data.MotRx1.TM_Gear == 2)
		{//R挡
			VehicleCmdCanTemp.B.Direction=0;
			VehicleCmdCanTemp.B.ReDirection = 1;
			VehicleCmdCanTemp.B.NeutralPosition = 0;
			//协议规定,R挡电动发负扭矩,此处保证送入底层电动为正扭矩
			RefTempTorq = 0 - RefTempTorq;
		}
		else
		{//N挡
			VehicleCmdCanTemp.B.Direction=0;
			VehicleCmdCanTemp.B.ReDirection = 0;	  
			VehicleCmdCanTemp.B.NeutralPosition = 1;
			RefTempTorq = 0;//空挡扭矩清零
		}


	#endif
//************************************挡位结构体赋值结束******************************************// 	
		RxTorRefValue = RefTempTorq;  //目标扭矩单位Nm
		//速度模式转速方向赋值(协议规定转速的正负代表方向)	  
		if(RxSpdRefValue >= 0)
		{//正转
			VehicleCmdCanTemp.B.FwdOrRev = 0;
		}
		else
		{//反转
			VehicleCmdCanTemp.B.FwdOrRev = 1;
		}
		

		//主动放电指令赋值	  
		// CtrlMode	起始位:2	长度:2	系数:1	偏移量:0	0:Reserved;1:Speed Control;2:Torque Control;3:Active Discharge
        if(g_SaeRxMsg[0].Data.MotRx1.CtrlMode == 3)
		{
			VehicleCmdCanTemp.B.mainctrl = 1;
		}
		else
		{
			VehicleCmdCanTemp.B.mainctrl = 0;  
		}