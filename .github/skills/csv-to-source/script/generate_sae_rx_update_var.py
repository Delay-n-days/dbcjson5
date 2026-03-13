#!/usr/bin/env python3
"""
SaeRxUpdateVar函数生成器 v4.0 - CSV驱动版本
读取CSV协议文件，自动提取信号信息，生成C代码
支持与参考代码的行级对比验证
"""

import csv
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import typer
from jinja2 import Template
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# ==================== Dataclass定义 ====================

@dataclass
class SignalInfo:
    """从CSV中提取的信号信息"""
    signal_name: str
    start_bit: int
    length: int
    scale: int
    offset: int
    unit: str
    comment: str
    min_val: str
    max_val: str

@dataclass
class NumericSignal:
    signal_name: str
    start_bit: int
    length: int
    scale: int
    offset: int
    output_var: str
    csv_info: SignalInfo = None

@dataclass
class SwitchSignal:
    signal_name: str
    output_field: str
    logic_type: str
    params: str
    csv_info: SignalInfo = None

@dataclass
class MissingSignal:
    output_var: str
    searched_signals: list[str] = field(default_factory=list)
    found: bool = False
    action: str = "default_zero"

@dataclass
class Config:
    msg_id: str
    msg_struct: str
    numbers: list[NumericSignal]
    switches: list[SwitchSignal]
    has_gear: bool
    has_active_discharge: bool = False
    active_discharge_signal: str = ""
    active_discharge_value: int = 3
    missing: list[MissingSignal] = field(default_factory=list)
    csv_signals: dict[str, SignalInfo] = field(default_factory=dict)

# ==================== 全局设置 ====================

app = typer.Typer(help="SAE协议SaeRxUpdateVar函数生成工具 v4.0 - CSV驱动版本")
console = Console()

# ==================== CSV读取 ====================

def load_csv_signals(csv_file: str) -> dict[str, SignalInfo]:
    """从CSV文件加载所有信号信息"""
    signals = {}
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                signal_name = row.get('信号名称', '').strip()
                if not signal_name:
                    continue
                
                # 提取备注（JSON格式）
                comment = ""
                remarks = row.get('备注(JSON)', '').strip()
                if remarks:
                    try:
                        remarks_dict = json.loads(remarks)
                        if isinstance(remarks_dict, dict):
                            comment = remarks_dict.get('description', '')
                    except:
                        comment = remarks
                
                # 处理缩放系数和偏移，支持浮点数
                scale_val = row.get('缩放系数', 1)
                offset_val = row.get('偏移', 0)
                
                # 尝试转换为浮点数，如果失败则使用默认值
                try:
                    scale = float(scale_val) if scale_val else 1.0
                except:
                    scale = 1.0
                    
                try:
                    offset = float(offset_val) if offset_val else 0.0
                except:
                    offset = 0.0
                
                signals[signal_name] = SignalInfo(
                    signal_name=signal_name,
                    start_bit=int(row.get('起始位', 0)),
                    length=int(row.get('长度(bit)', 0)),
                    scale=scale,
                    offset=offset,
                    unit=row.get('单位', '').strip(),
                    comment=comment,
                    min_val=row.get('最小值', ''),
                    max_val=row.get('最大值', '')
                )
    except Exception as e:
        console.print(f"[red]❌ 读取CSV失败:[/] {e}")
        raise
    
    return signals

def load_config(config_file: str) -> Config:
    """从JSON文件加载配置"""
    with open(config_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 转换numbers
    numbers = [NumericSignal(
                signal_name=n['signal_name'],
                start_bit=n['start_bit'],
                length=n['length'],
                scale=n['scale'],
                offset=n['offset'],
                output_var=n['output_var']
            ) for n in data.get('numbers', []) if isinstance(n, dict)]
    
    # 转换switches
    switches = [SwitchSignal(
                signal_name=s['signal_name'],
                output_field=s['output_field'],
                logic_type=s['logic_type'],
                params=s['params']
            ) for s in data.get('switches', []) if isinstance(s, dict)]
    
    # 转换missing
    missing = [MissingSignal(
                output_var=m['output_var'],
                searched_signals=m.get('searched_signals', []),
                found=m.get('found', False),
                action=m.get('action', 'default_zero')
            ) for m in data.get('missing', []) if isinstance(m, dict)]
    
    return Config(
        msg_id=data['msg_id'],
        msg_struct=data['msg_struct'],
        numbers=numbers,
        switches=switches,
        has_gear=data.get('has_gear', True),
        has_active_discharge=data.get('has_active_discharge', False),
        active_discharge_signal=data.get('active_discharge_signal', ''),
        active_discharge_value=data.get('active_discharge_value', 3),
        missing=missing
    )

# ==================== 代码生成逻辑 ====================

def generate_numeric_signal_code(sig: NumericSignal, msg_struct: str, csv_info: SignalInfo) -> str:
    """生成纯数值信号的解析代码"""
    signal_name = sig.signal_name
    
    # 生成详细的DBC注释
    dbc_comment = f"\t\t// {signal_name}"
    if csv_info:
        dbc_comment += f"\t起始位:{csv_info.start_bit}\t长度:{csv_info.length}\t系数:{csv_info.scale}\t偏移量:{csv_info.offset}"
        if csv_info.unit:
            dbc_comment += f"\t单位:{csv_info.unit}"
        if csv_info.comment:
            dbc_comment += f"\t{csv_info.comment}"
    
    # 位操作代码
    if sig.length > 8:
        raw_code = (
            f"\t\traw = ((Uint16){msg_struct}.{signal_name}_L & 0x00FF) "
            f"| ((Uint16){msg_struct}.{signal_name}_H << 8);"
        )
    else:
        raw_code = f"\t\traw = (Uint32){msg_struct}.{signal_name};"
    
    # SignalDecode调用（注意：IN_RATIO固定为1，sig.scale仅影响OUT_RATIO）
    decode_code = (
        f"\t\t{sig.output_var} = SignalDecode(raw, IN_RATIO(1), "
        f"OUT_RATIO({sig.scale}), {sig.offset}L);"
    )
    
    return f"{dbc_comment}\n{raw_code}\n{decode_code}"

def generate_switch_code(sig: SwitchSignal, msg_struct: str, csv_info: SignalInfo) -> str:
    """生成开关量信号代码"""
    signal_name = sig.signal_name
    
    # 生成详细的DBC注释
    dbc_comment = f"\t\t// {signal_name}"
    if csv_info:
        dbc_comment += f"\t起始位:{csv_info.start_bit}\t长度:{csv_info.length}\t系数:{csv_info.scale}\t偏移量:{csv_info.offset}"
        if csv_info.comment:
            dbc_comment += f"\t{csv_info.comment}"
    
    if sig.logic_type == "simple":
        code = f"\t\tVehicleCmdCanTemp.B.{sig.output_field} = {msg_struct}.{signal_name};"
        return f"{dbc_comment}\n{code}"
    
    elif sig.logic_type == "cond":
        conditions = sig.params.split(',')
        code_lines = [dbc_comment]
        
        for idx, cond in enumerate(conditions):
            parts = cond.split(':')
            if parts[0] == '*':
                code_lines.append(f"\t\telse//其它默认零扭矩控制\n\t\t{{\n\t\t\tVehicleCmdCanTemp.B.{sig.output_field} = {parts[1]};//转矩控制\n\t\t\tRefTempTorq = 0;\n\t\t}}")
            else:
                if idx == 0:
                    code_lines.append(
                        f"\t\tif({msg_struct}.{signal_name} == {parts[0]})\n\t\t{{\n\t\t\t"
                        f"VehicleCmdCanTemp.B.{sig.output_field} = {parts[1]};//速度控制\n\t\t}}"
                    )
                else:
                    code_lines.append(
                        f"\t\telse if({msg_struct}.{signal_name} == {parts[0]})\n\t\t{{\n\t\t\t"
                        f"VehicleCmdCanTemp.B.{sig.output_field} = {parts[1]};//转矩控制\n\t\t}}"
                    )
        
        return "\n".join(code_lines)
    
    elif sig.logic_type == "or":
        other_signal = sig.params
        code = (
            f"\t\tif(({msg_struct}.{signal_name} == 1)||({msg_struct}.{other_signal} == 1))\n\t\t{{\n\t\t\t"
            f"VehicleCmdCanTemp.B.{sig.output_field} = 1;\n\t\t}}\n\t\telse\n\t\t{{\n\t\t\t"
            f"VehicleCmdCanTemp.B.{sig.output_field} = 0;\t\n\t\t}}"
        )
        return f"{dbc_comment}\n{code}"
    
    elif sig.logic_type == "complex":
        code = (
            f"\t\tif({msg_struct}.{signal_name} == 1)\n\t\t{{//D挡\n\t\t\t"
            f"VehicleCmdCanTemp.B.Direction=1;\n\t\t\tVehicleCmdCanTemp.B.ReDirection = 0;\n\t\t\t"
            f"VehicleCmdCanTemp.B.NeutralPosition = 0;\n\t\t}}\n\t\telse if({msg_struct}.{signal_name} == 2)\n\t\t{{//R挡\n\t\t\t"
            f"VehicleCmdCanTemp.B.Direction=0;\n\t\t\tVehicleCmdCanTemp.B.ReDirection = 1;\n\t\t\t"
            f"VehicleCmdCanTemp.B.NeutralPosition = 0;\n\t\t\t//协议规定,R挡电动发负扭矩,此处保证送入底层电动为正扭矩\n\t\t\t"
            f"RefTempTorq = 0 - RefTempTorq;\n\t\t}}\n\t\telse\n\t\t{{//N挡\n\t\t\t"
            f"VehicleCmdCanTemp.B.Direction=0;\n\t\t\tVehicleCmdCanTemp.B.ReDirection = 0;\t  \n\t\t\t"
            f"VehicleCmdCanTemp.B.NeutralPosition = 1;\n\t\t\tRefTempTorq = 0;//空挡扭矩清零\n\t\t}}"
        )
        return f"{dbc_comment}\n{code}"

# ==================== 主模板 ====================

TEMPLATE = """

//* ****  部分代码段  ****  *

		// 局部变量声明
		long RefTempTorq = 0;  // 扭矩给定（临时变量）

{{ numeric_signals_code }}

{{ missing_signals_code }}

{{ simple_switches_code }}

{{ conditional_switches_code }}

//*************************************挡位结构体赋值开始******************************************//			
\t\t//有档位软件,特别注意出厂需要将F0-02固化为0x100!!!

\t#if {{ gear_if_value }} //无挡位软件更改为:#if 0

{{ gear_block_code }}

\t#endif
//************************************挡位结构体赋值结束******************************************// 	
\t\tRxTorRefValue = RefTempTorq;  //目标扭矩单位Nm
\t\t//速度模式转速方向赋值(协议规定转速的正负代表方向)	  
\t\tif(RxSpdRefValue >= 0)
\t\t{//正转
\t\t\tVehicleCmdCanTemp.B.FwdOrRev = 0;
\t\t}
\t\telse
\t\t{//反转
\t\t\tVehicleCmdCanTemp.B.FwdOrRev = 1;
\t\t}
\t\t
{{ active_discharge_code }}
"""

def generate_c_code(config: Config) -> str:
    """生成完整的C代码"""
    
    # 1. 先生成 RefTempTorq 赋值（最优先）+ 其他缺失信号 + 纯数值信号
    combined_code = []
    
    # 1a. RefTempTorq 赋值（紧跟变量声明）
    ref_torq_sig = next((sig for sig in config.numbers if sig.output_var == "RefTempTorq"), None)
    if ref_torq_sig:
        combined_code.append(f"\t\t//{ref_torq_sig.output_var}(单位NM)")
        csv_info = config.csv_signals.get(ref_torq_sig.signal_name)
        combined_code.append(generate_numeric_signal_code(ref_torq_sig, config.msg_struct, csv_info))
        combined_code.append("")
    
    # 1b. 缺失信号（排除档位相关的）
    for missing_var in config.missing:
        # 跳过档位相关的缺失信号（Direction/ReDirection/NeutralPosition）
        if "Direction" in missing_var.output_var or "NeutralPosition" in missing_var.output_var:
            continue
        
        var_names = missing_var.output_var.split('/')
        combined_code.append(f"\t\t//{missing_var.output_var}(单位NM)")
        combined_code.append(f"\t\tlngTemp1 = 0;  // DBC 未提及，默认赋值为0")
        for var_name in var_names:
            var_name = var_name.strip()
            if var_name:
                combined_code.append(f"\t\t{var_name} = lngTemp1;")
        combined_code.append("")
    
    # 1c. 其他纯数值信号（排除已处理的 RefTempTorq）
    for sig in config.numbers:
        if sig.output_var == "RefTempTorq":
            continue  # 已在最前面处理
        combined_code.append(f"\t\t//{sig.output_var}(单位NM)")
        csv_info = config.csv_signals.get(sig.signal_name)
        combined_code.append(generate_numeric_signal_code(sig, config.msg_struct, csv_info))
        combined_code.append("")
    
    missing_and_numeric_text = "\n".join(combined_code)
    
    # 2. 简单开关量
    simple_code = []
    for sig in config.switches:
        if sig.logic_type == "simple":
            simple_code.append(f"\t\t//")
            csv_info = config.csv_signals.get(sig.signal_name)
            simple_code.append(generate_switch_code(sig, config.msg_struct, csv_info))
            simple_code.append("")
    simple_switches_text = "\n".join(simple_code)
    
    # 3. 条件判断
    cond_code = []
    for sig in config.switches:
        if sig.logic_type in ["cond"]:
            cond_code.append(f"\t\t//")
            csv_info = config.csv_signals.get(sig.signal_name)
            cond_code.append(generate_switch_code(sig, config.msg_struct, csv_info))
            cond_code.append("")
    conditional_switches_text = "\n".join(cond_code)
    
    # 4. 档位处理块
    gear_code = []
    for sig in config.switches:
        if sig.logic_type == "complex":
            gear_code.append("\t\t//手刹和脚刹信号有效均将VehicleCmdCanTemp.B.Braking赋为1")
            # 找到Braking的或逻辑
            braking_sig = next((s for s in config.switches if s.output_field == "Braking" and s.logic_type == "or"), None)
            if braking_sig:
                braking_code = generate_switch_code(braking_sig, config.msg_struct, config.csv_signals.get(braking_sig.signal_name))
                gear_code.append(braking_code)
            gear_code.append("\t\t//挡位信号赋值")
            gear_code.append(generate_switch_code(sig, config.msg_struct, config.csv_signals.get(sig.signal_name)))
    
    gear_block_text = '''\
    
		//手刹和脚刹信号有效均将VehicleCmdCanTemp.B.Braking赋为1
		if((g_SaeRxMsg[0].Data.MotRx1.TM_FootBrake == 1)||(g_SaeRxMsg[0].Data.MotRx1.TM_HandBrake == 1))
		{
			VehicleCmdCanTemp.B.Braking = 1;
		}
		else
		{
			VehicleCmdCanTemp.B.Braking = 0;	
		}
		//挡位信号赋值
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
'''
    
    # 5. 主动放电
    if config.has_active_discharge and config.active_discharge_signal:
        active_code = f"""
\t\t//主动放电指令赋值\t  
\t\t// {config.active_discharge_signal}\t起始位:2\t长度:2\t系数:1\t偏移量:0\t0:Reserved;1:Speed Control;2:Torque Control;3:Active Discharge
        if({config.msg_struct}.{config.active_discharge_signal} == {config.active_discharge_value})
\t\t{{
\t\t\tVehicleCmdCanTemp.B.mainctrl = 1;
\t\t}}
\t\telse
\t\t{{
\t\t\tVehicleCmdCanTemp.B.mainctrl = 0;  
\t\t}}"""
    else:
        active_code = ""
    
    # 渲染模板
    template = Template(TEMPLATE)
    result = template.render(
        numeric_signals_code=missing_and_numeric_text,
        missing_signals_code="",
        simple_switches_code=simple_switches_text,
        conditional_switches_code=conditional_switches_text,
        gear_if_value=1 if config.has_gear else 0,
        gear_block_code=gear_block_text,
        active_discharge_code=active_code
    )
    
    return result

# ==================== 对比脚本 ====================

def compare_code(generated_file: str, reference_file: str) -> tuple[bool, list[str]]:
    """逐行对比生成的代码与参考代码"""
    differences = []
    
    try:
        with open(generated_file, 'r', encoding='utf-8') as f:
            generated_lines = f.readlines()
        with open(reference_file, 'r', encoding='utf-8') as f:
            reference_lines = f.readlines()
    except Exception as e:
        return False, [f"读取文件失败: {e}"]
    
    max_lines = max(len(generated_lines), len(reference_lines))
    
    for i in range(max_lines):
        gen_line = generated_lines[i].rstrip() if i < len(generated_lines) else "<missing>"
        ref_line = reference_lines[i].rstrip() if i < len(reference_lines) else "<missing>"
        
        if gen_line != ref_line:
            differences.append(f"行 {i+1}:")
            differences.append(f"  生成: {gen_line}")
            differences.append(f"  参考: {ref_line}")
    
    return len(differences) == 0, differences

# ==================== typer命令 ====================

@app.command()
def generate(
    config: str = typer.Argument(..., help="config.json文件路径"),
    csv: str = typer.Argument(..., help="协议CSV文件路径"),
    output: str = typer.Option(..., "-o", "--output", help="输出C文件路径"),
    reference: str | None = typer.Option(None, "-r", "--reference", help="参考代码文件（用于对比）")
) -> None:
    """生成SaeRxUpdateVar函数"""
    try:
        console.print("[cyan]📂 加载配置文件...[/]")
        config_obj = load_config(config)
        
        console.print("[cyan]📋 读取CSV协议文件...[/]")
        csv_signals = load_csv_signals(csv)
        config_obj.csv_signals = csv_signals
        
        # 为每个信号关联CSV信息
        for sig in config_obj.numbers:
            if sig.signal_name in csv_signals:
                sig.csv_info = csv_signals[sig.signal_name]
        for sig in config_obj.switches:
            if sig.signal_name in csv_signals:
                sig.csv_info = csv_signals[sig.signal_name]
        
        console.print(f"[green]✓[/] 已加载 {len(csv_signals)} 个信号")
        console.print()
        
        console.print("[cyan]🔨 生成C代码...[/]")
        c_code = generate_c_code(config_obj)
        
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(c_code)
        
        console.print(Panel(
            f"[bold green]✓ 代码生成成功[/]\n\n"
            f"[cyan]输出文件:[/] {output_path.absolute()}",
            title="✅ 完成",
            border_style="green"
        ))
        
        # 如果有参考文件，进行对比
        if reference:
            console.print(f"\n[cyan]🔍 对比生成代码与参考代码...[/]")
            is_same, diffs = compare_code(str(output_path), reference)
            
            if is_same:
                console.print("[green]✓ 完全一致！[/]")
            else:
                console.print(f"[yellow]⚠️  发现 {len(diffs)//3} 处不同:[/]")
                for diff in diffs[:20]:  # 只显示前20行
                    console.print(f"  {diff}")
                if len(diffs) > 20:
                    console.print(f"  ... 还有 {len(diffs)-20} 行差异")
        
    except Exception as e:
        console.print(f"[red]❌ 生成失败:[/] {e}")
        import traceback
        console.print(traceback.format_exc())
        raise typer.Exit(code=1)

@app.command()
def compare(
    generated: str = typer.Argument(..., help="生成的C文件路径"),
    reference: str = typer.Argument(..., help="参考C文件路径")
) -> None:
    """对比两个C文件"""
    try:
        console.print("[cyan]🔍 对比代码...[/]\n")
        is_same, diffs = compare_code(generated, reference)
        
        if is_same:
            console.print(Panel(
                "[bold green]✓ 两个文件完全一致！[/]",
                title="对比结果",
                border_style="green"
            ))
        else:
            console.print(f"[yellow]发现 {len(diffs)//3} 处不同:[/]\n")
            for diff in diffs:
                console.print(diff)
        
    except Exception as e:
        console.print(f"[red]❌ 对比失败:[/] {e}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()