#!/usr/bin/env python3
"""
DBC to C Header 转换工具
从 DBC 文件生成 C 语言头文件（结构体定义）
"""

import csv
import json
import re
from pathlib import Path
from typing import Dict, List, Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

app = typer.Typer(help="DBC 到 C 头文件转换工具")
console = Console()


# ==================== 参数验证函数 ====================
def validate_baud_rate(baud_rate: int) -> int:
    """验证波特率参数"""
    if baud_rate not in [250, 500]:
        raise typer.BadParameter(f"波特率必须是 250 或 500,当前值: {baud_rate}")
    return baud_rate


def validate_rx_ids(rx_ids: List[str]) -> List[str]:
    """验证接收帧ID参数"""
    if not rx_ids:
        raise typer.BadParameter("必须提供至少一个接收帧ID (使用 --rx-id)")
    
    validated = []
    for rx_id in rx_ids:
        # 验证格式 (支持 0x 或 0X 开头的十六进制)
        if not re.match(r'^0[xX][0-9A-Fa-f]+$', rx_id):
            raise typer.BadParameter(
                f"接收帧ID格式错误: '{rx_id}', 应为十六进制格式 (如 0x0CFF05EF)"
            )
        validated.append(rx_id)
    
    return validated


# ==================== 用户提供的位域处理代码 ====================
class HtextExec:
    """联合体字符处理类"""
    def __init__(
        self,
        varName: str = None,
        bitLength: str = None,
        explain: str = None,
        strr: str = None,
    ):
        if strr is not None:
            strr = strr + " "
            try:
                Arr = strr.split("//")
                Arr2 = Arr[0].split(" ")
                self.varName = Arr2[0]
                self.bitLength = Arr2[1]
                if Arr[1][0] == " ":
                    self.explain = Arr[1][1:]
                else:
                    self.explain = Arr[1]
            except:
                self.varName = " "
                self.bitLength = "0"
                self.explain = " "
        else:
            self.varName = varName
            self.bitLength = bitLength
            self.explain = explain

    def printt(self, SpaceNum):
        Space = ""
        for i in range(SpaceNum):
            Space = Space + " "
        return (
            "    unsigned "
            + self.varName
            + Space
            + ": "
            + self.bitLength
            + "; "
            + "// "
            + self.explain
            + "\n"
        )


def createstructYCL(a):
    """预处理 - 填充预留位"""
    Mode = 1
    a = a.replace("\t", " ")
    while "  " in a:
        a = a.replace("  ", " ")
    strList = a.split("\n")
    for Arr in strList:
        if Arr != "":
            Arr = Arr.split("//")
            Arr2 = Arr[0].split(" ")
            if len(Arr2) > 3:
                Mode = 2
                break
            else:
                Mode = 1
                break
    if Mode == 2:
        ret = ""
        startA = 0
        ResNum = 1
        for i in strList:
            varName = ""
            bitLength = ""
            explain = ""
            startbit = ""
            if i != "":
                Arr = i.split("//")
                Arr2 = Arr[0].split(" ")
                varName = Arr2[0]
                bitLength = Arr2[2]
                startbit = Arr2[1]
                if Arr[1][0] == " ":
                    explain = Arr[1][1:]
                else:
                    explain = Arr[1]
                lengthres = int(startbit) - startA
                if lengthres != 0:
                    while lengthres > 8:
                        sub = 8 - startA % 8
                        ret += "Res" + str(ResNum) + " " + str(sub) + " // 预留\n"
                        ResNum += 1
                        lengthres = lengthres - sub
                        startA += int(sub)
                    sub2 = 8 - startA % 8
                    if lengthres > sub2 and sub2 != 0:
                        ret += "Res" + str(ResNum) + " " + str(sub2) + " // 预留\n"
                        lengthres = lengthres - sub2
                        startA += sub2
                        ResNum += 1
                    ret += "Res" + str(ResNum) + " " + str(lengthres) + " // 预留\n"
                    ResNum += 1
                    startA += int(lengthres)
                    ret += varName + " " + bitLength + " " + "// " + explain + "\n"
                    startA += int(bitLength)
                else:
                    ret += varName + " " + bitLength + " " + "// " + explain + "\n"
                    startA += int(bitLength)
        if startA != 64:
            lengthres = 64 - startA
            while lengthres != 0:
                sub = 8 - startA % 8
                ret += "Res" + str(ResNum) + " " + str(sub) + " // 预留\n"
                ResNum += 1
                lengthres = lengthres - sub
                startA += int(sub)
        return ret
    else:
        return a


def createstruct(source):
    """生成结构体定义"""
    a = createstructYCL(source)
    b = ""
    varNameLength = 0
    sub = 0
    _Byte = 1
    subList = []
    lensub = 0
    a = a.strip() + " "
    a = a.replace("\t", " ")
    while "  " in a:
        a = a.replace("  ", " ")
    Arr = a.split("\n")
    b = b + "    // Byte0 ---------------------------------------------------\n"
    for str1 in Arr:
        Arr2 = HtextExec(strr=str1)
        if int(Arr2.bitLength) > 8:
            varNameLength = max(varNameLength, len(Arr2.varName) + 2)
        else:
            varNameLength = max(varNameLength, len(Arr2.varName))
    for str1 in Arr:
        Arr2 = HtextExec(strr=str1)
        k = 8 - lensub % 8
        if int(Arr2.bitLength) > 8:
            subArr2_1 = HtextExec(
                varName=Arr2.varName + "_L", bitLength=str(k), explain=Arr2.explain
            )
            subList.append(subArr2_1)
            lensub += int(subArr2_1.bitLength)
            subArr2_2 = HtextExec(
                varName=Arr2.varName + "_H",
                bitLength=str(int(Arr2.bitLength) - k),
                explain=Arr2.explain,
            )
            subList.append(subArr2_2)
            lensub += int(subArr2_2.bitLength)
        else:
            subList.append(Arr2)
            lensub += int(Arr2.bitLength)
    
    # ========== 添加验证：检查总位数 ==========
    total_bits = sum(int(obj.bitLength) for obj in subList)
    if total_bits != 64:
        raise ValueError(f"位数验证失败！总位数为 {total_bits}，应为 64 位")
    
    for obj in subList:
        sub = sub + int(obj.bitLength)
        b = b + obj.printt(varNameLength - len(obj.varName))
        if sub / 8 == _Byte:
            _Byte = _Byte + 1
            if _Byte < 9:
                b = (
                    b
                    + "    // Byte"
                    + str(_Byte - 1)
                    + " ---------------------------------------------------\n"
                )
    return ("代码生成成功✅!", "success", b)


# ==================== DBC 解析和转换逻辑 ====================
def parse_comment_json(comment_str: str) -> dict:
    """解析JSON格式的注释"""
    try:
        return json.loads(comment_str) if comment_str else {}
    except:
        return {}


def format_signal_comment(signal: dict) -> str:
    """格式化信号注释"""
    comment_json = parse_comment_json(signal.get('comment', ''))
    
    if not comment_json:
        return ""
    
    # 如果有枚举值
    if any(k.isdigit() for k in comment_json.keys()):
        enum_parts = []
        for k, v in sorted(comment_json.items(), key=lambda x: (not x[0].isdigit(), x[0])):
            if k.isdigit():
                enum_parts.append(f"{k}:{v}")
        return "; ".join(enum_parts)
    
    # 如果有描述
    if 'description' in comment_json:
        return comment_json['description']
    
    return ""


def csv_to_signal_list(csv_file: str, encoding: str = 'utf-8') -> Dict[str, List]:
    """从CSV读取信号列表，按消息分组"""
    messages = {}
    
    with open(csv_file, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f)
        for row in reader:
            msg_name = row['消息名称']
            
            if msg_name not in messages:
                messages[msg_name] = {
                    'id': row['消息ID'],
                    'length': int(row['消息长度']),
                    'period': row['周期时间(ms)'],
                    'sender': row['发送者'],
                    'signals': []
                }
            
            comment = format_signal_comment({
                'comment': row.get('备注(JSON)', '')
            })
            
            messages[msg_name]['signals'].append({
                'name': row['信号名称'],
                'start_bit': int(row['起始位']),
                'length': int(row['长度(bit)']),
                'comment': comment
            })
    
    return messages


def generate_struct_input(signals: List[dict]) -> str:
    """生成createstruct所需的输入格式"""
    lines = []
    for sig in sorted(signals, key=lambda x: x['start_bit']):
        line = f"{sig['name']} {sig['start_bit']} {sig['length']} // {sig['comment']}"
        lines.append(line)
    return "\n".join(lines)


def determine_message_type(sender: str, msg_name: str) -> tuple:
    """判断消息是接收还是发送"""
    # 根据发送者判断
    if sender.upper() in ['HCU', 'VCU', 'BMS']:
        return ('RX', 'MOT_RX_APP')
    else:
        return ('TX', 'MOTOR_TX')


def print_generation_summary(
    baud_rate: int,
    messages: Dict,
    rx_ids: List[str]
):
    """打印生成汇总信息"""
    # 【重要】根据 rx_ids 参数重新分类消息：
    # - 如果消息 ID 在 rx_ids 中，则为接收消息
    # - 其他所有消息都为发送消息
    rx_messages = []
    tx_messages = []
    
    for name, data in messages.items():
        msg_id = data.get('id', '')
        if msg_id in rx_ids:
            rx_messages.append((name, data))
        else:
            tx_messages.append((name, data))
    
    # 统计信号数量
    rx_signal_count = sum(len(data['signals']) for _, data in rx_messages)
    tx_signal_count = sum(len(data['signals']) for _, data in tx_messages)
    
    # 创建汇总表格
    table = Table(title="生成汇总", show_header=False, border_style="cyan")
    table.add_column("项目", style="cyan", width=20)
    table.add_column("详情", style="white")
    
    table.add_row("波特率", f"{baud_rate}K")
    table.add_row("接收帧ID", ", ".join(rx_ids))
    
    # 接收报文详情（报文ID + 报文名称 + 周期）
    rx_details = []
    for msg_name, msg_data in rx_messages:
        msg_id = msg_data.get('id', 'N/A')
        period = msg_data.get('period', 'N/A')
        rx_details.append(f"  • {msg_id} {msg_name} (周期: {period}ms)")
    rx_summary = f"{len(rx_messages)}个\n" + "\n".join(rx_details) if rx_details else "0个"
    table.add_row("接收报文", rx_summary)
    
    # 发送报文详情（报文ID + 报文名称 + 周期）
    tx_details = []
    for msg_name, msg_data in tx_messages:
        msg_id = msg_data.get('id', 'N/A')
        period = msg_data.get('period', 'N/A')
        tx_details.append(f"  • {msg_id} {msg_name} (周期: {period}ms)")
    tx_summary = f"{len(tx_messages)}个\n" + "\n".join(tx_details) if tx_details else "0个"
    table.add_row("发送报文", tx_summary)
    
    table.add_row("接收信号", f"{rx_signal_count}个")
    table.add_row("发送信号", f"{tx_signal_count}个")
    
    console.print("")
    console.print(table)
    console.print("")


def generate_header_file(
    messages: Dict, 
    project_name: str = "Motor",
    baud_rate: int = 250,
    rx_ids: List[str] = None
) -> str:
    """生成完整的.h文件"""
    if rx_ids is None:
        rx_ids = []
    
    # 【重要】根据 rx_ids 参数重新分类消息：
    # - 如果消息 ID 在 rx_ids 中，则为接收消息
    # - 其他所有消息都为发送消息
    rx_messages = []
    tx_messages = []
    
    for msg_name, msg_data in messages.items():
        msg_id = msg_data.get('id', '')
        if msg_id in rx_ids:
            rx_messages.append((msg_name, msg_data))
        else:
            tx_messages.append((msg_name, msg_data))
    
    # 验证：接收和发送报文数量不能为0
    if len(rx_messages) == 0:
        raise typer.BadParameter(
            f"接收报文数量为 0！\n"
            f"  指定的接收帧ID: {', '.join(rx_ids)}\n"
            f"  可用的消息ID: {', '.join([data.get('id', 'N/A') for _, data in messages.items()])}\n"
            f"  请检查 --rx-id 参数是否与CSV/DBC中的消息ID匹配"
        )
    
    if len(tx_messages) == 0:
        raise typer.BadParameter(
            f"发送报文数量为 0！\n"
            f"  所有消息都被指定为接收消息，这通常是配置错误。\n"
            f"  请检查 --rx-id 参数是否过多"
        )
    
    # ========== 开始生成头文件 ==========
    header = []
    
    # 宏定义部分
    header.append("//*********************************** 宏定义 *********************************************//")
    header.append("//*********************************** CAN通讯接收数据帧个数 *********************************************//")
    header.append(f"#define SAE_MAX_RX_NUM  \t\t{len(rx_messages)}")
    header.append("")
    header.append("//*********************************** CAN通讯发送数据帧个数 *******************************************//")
    header.append(f"#define SAE_MAX_TX_NUM  \t\t{len(tx_messages)}\t//注意此处为协议定义发送个数,不用预留")
    header.append("")
    header.append("//*********************************** CAN通讯数据帧格式 *********************************************//")
    
    # 判断是否使用扩展帧
    has_extended = any(int(msg[1]['id'], 16) > 0x7FF for msg in list(rx_messages) + list(tx_messages))
    header.append(f"#define EXIDEEN   \t\t\t\t{1 if has_extended else 0}   // 0:无效 1:使能扩展帧")
    header.append(f"#define STDIDEEN   \t\t\t\t{0 if has_extended else 1}   // 0:无效 1:使能标准帧")
    header.append("")
    header.append("//*********************************** CAN通讯波特率设置 ***********************************************//")
    baud_250_value = 1 if baud_rate == 250 else 0
    baud_500_value = 1 if baud_rate == 500 else 0
    header.append(f"#define BAUD250\t\t\t\t\t{baud_250_value}   // 0:无效 1:250K波特率")
    header.append(f"#define BAUD500\t\t\t\t\t{baud_500_value}   // 0:无效 1:500K波特率")
    header.append("")
    
    # 接收帧ID定义
    header.append("//******************************CAN通讯接收帧ID*******************************************//")
    # 使用传入的 rx_ids 参数
    actual_rx_ids = rx_ids if rx_ids else [msg_data['id'] for _, msg_data in rx_messages]
    for idx, rx_id in enumerate(actual_rx_ids, 1):
        # 查找对应的消息名（如果有）
        msg_name = ""
        sender = ""
        for name, data in rx_messages:
            if data['id'] == rx_id:
                msg_name = name
                sender = data.get('sender', '')
                break
        if not msg_name and idx <= len(rx_messages):
            msg_name = rx_messages[idx-1][0]
            sender = rx_messages[idx-1][1].get('sender', '')
        
        # 简化宏名称：EVCU1, EVCU2 等或 MSG1, MSG2
        macro_name = f"EVCU{idx}" if sender.upper() in ['HCU', 'VCU', 'BMS'] else f"MSG{idx}"
        header.append(f"#define CAN_ID_{macro_name} \t\t\t((unsigned long){rx_id})\t// 接收VCU帧ID,ID={rx_id}")
    header.append("")
    
    # 发送周期定义
    header.append("//*************************** CAN通讯发送数据帧周期(单位ms)*******************************//")
    for idx, (msg_name, msg_data) in enumerate(tx_messages):
        period = msg_data.get('period', '10')
        header.append(f"#define MCUMSGTX{idx}TIME\t\t\t{period}\t//报文发送周期")
    header.append("")
    
    # 结构体定义
    header.append("//*************************** CAN通讯数据帧结构体定义 ************************************//")
    
    # 生成接收报文结构体
    for idx, (msg_name, msg_data) in enumerate(rx_messages, 1):
        header.append(f"// 接收报文{idx} :{msg_name}")
        header.append(f"typedef struct __MOT_RX_APP{idx}       ")
        header.append("{")
        
        # 生成信号输入
        signal_input = generate_struct_input(msg_data['signals'])
        _, _, struct_body = createstruct(signal_input)
        header.append(struct_body.rstrip('\n'))
        header.append("")
        header.append("")
        header.append(f"}}TYPE_MOT_RX_APP{idx};")
        header.append("")
    
    # 生成发送报文结构体
    for idx, (msg_name, msg_data) in enumerate(tx_messages, 1):
        msg_id = msg_data['id']  # 保持原始大小写
        period = msg_data.get('period', '10')
        
        header.append(f"// 发送报文{idx}：{msg_name}")
        header.append(f"// ID = {msg_id}")
        header.append(f"// T={period}ms")
        header.append(f"typedef struct __MOTOR_TX{idx}")
        header.append("{")
        
        # 生成信号输入
        signal_input = generate_struct_input(msg_data['signals'])
        _, _, struct_body = createstruct(signal_input)
        header.append(struct_body.rstrip('\n'))
        header.append(f"}}TYPE_MOT_TX{idx};")
        header.append("")
        header.append("")
    
    # Union定义
    header.append("typedef union __SAE_DATA")
    header.append("{")
    header.append("\tunsigned int WordArray[4];")
    header.append("\tSAE_Bytes Bytes;")
    
    for idx, (msg_name, _) in enumerate(rx_messages, 1):
        header.append(f"\tTYPE_MOT_RX_APP{idx} MotRx{idx};  // {msg_name} ")
    
    for idx, (msg_name, _) in enumerate(tx_messages, 1):
        header.append(f"\tTYPE_MOT_TX{idx} MotTx{idx}; // {msg_name}")
    
    header.append("}SAE_DATA;")
    header.append("")
    
    return "\n".join(header)


@app.command("dbc", help="从 DBC 文件生成 C 头文件 (先转CSV再生成)")
def from_dbc(
    dbc_file: str = typer.Argument(..., help="DBC文件路径"),
    output: str = typer.Option(None, "-o", "--output", help="输出的.h文件路径"),
    baud_rate: int = typer.Option(..., "--baud", "--baud-rate", help="CAN波特率 (250 或 500)", callback=lambda x: validate_baud_rate(x)),
    rx_ids: List[str] = typer.Option(..., "--rx-id", help="接收帧ID (十六进制,如 0x0CFF05EF,可多次指定)"),
    dbc_encoding: str = typer.Option("gb2312", "-e", "--encoding", help="DBC 文件编码"),
    project_name: str = typer.Option("Motor", "-p", "--project", help="项目名称"),
):
    """
    将 DBC 文件转换为 C 头文件
    
    示例:
        uv run python scripts/dbc2header.py outputs/motor.dbc -o outputs/motor.h
    """
    try:
        # 1. DBC → CSV（直接调用函数而不是subprocess）
        console.print("[cyan]步骤 1/3: 转换 DBC 到 CSV...[/cyan]")
        
        # 导入dbc2csv模块（同目录）
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from dbc2csv import dbc_to_unified_csv
        
        csv_file = Path(dbc_file).with_suffix('.csv')
        
        # 直接调用函数而不是subprocess
        dbc_to_unified_csv(
            dbc_file=dbc_file,
            output_csv=str(csv_file),
            encoding=dbc_encoding
        )
        
        # 2. 解析CSV
        console.print("[cyan]步骤 2/3: 解析 CSV 数据...[/cyan]")
        messages = csv_to_signal_list(str(csv_file))
        console.print(f"  找到 {len(messages)} 个消息")
        
        # 3. 生成.h文件
        console.print("[cyan]步骤 3/3: 生成 C 头文件...[/cyan]")
        header_content = generate_header_file(messages, project_name, baud_rate, rx_ids)
        
        # 确定输出文件名
        if output is None:
            output = Path(dbc_file).with_suffix('.h')
        
        # 写入文件
        with open(output, 'w', encoding='utf-8') as f:
            f.write(header_content)
        
        console.print(f"[green]✓ 成功生成头文件: {output}[/green]")
        
        # 打印生成汇总
        print_generation_summary(baud_rate, messages, rx_ids)
        
        # 清理临时CSV
        if csv_file.exists():
            csv_file.unlink()
        
        # 清理临时CSV
        if csv_file.exists():
            csv_file.unlink()
        
    except ValueError as e:
        console.print(f"[red]错误: {e}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]转换失败: {e}[/red]")
        import traceback
        traceback.print_exc()
        raise typer.Exit(code=1)


@app.command("csv", help="从 CSV 文件生成 C 头文件 (推荐:跳过DBC转换,由AI提取参数)")
def from_csv(
    csv_file: str = typer.Argument(..., help="CSV文件路径 (统一格式)"),
    output: str = typer.Option(None, "-o", "--output", help="输出的.h文件路径"),
    baud_rate: int = typer.Option(..., "--baud", "--baud-rate", help="CAN波特率 (250 或 500,由AI从文档提取)", callback=lambda x: validate_baud_rate(x)),
    rx_ids: List[str] = typer.Option(..., "--rx-id", help="接收帧ID (十六进制,由AI从文档提取,可多次指定)"),
    project_name: str = typer.Option("Motor", "-p", "--project", help="项目名称"),
):
    """从 CSV 文件直接生成 C 头文件 (优先使用此命令)
    
    注意:
    - 波特率和接收帧ID应由大模型从协议文档中提取后输入
    - CSV文件格式应为统一格式 (19列)
    - 此命令跳过DBC转换步骤,更高效
    """
    try:
        # 验证参数
        rx_ids = validate_rx_ids(rx_ids)
        
        # 1. 解析CSV
        console.print("[cyan]步骤 1/2: 解析 CSV 数据...[/cyan]")
        messages = csv_to_signal_list(csv_file)
        console.print(f"  找到 {len(messages)} 个消息")
        
        # 2. 生成.h文件
        console.print("[cyan]步骤 2/2: 生成 C 头文件...[/cyan]")
        header_content = generate_header_file(messages, project_name, baud_rate, rx_ids)
        
        # 确定输出文件名
        if output is None:
            output = Path(csv_file).with_suffix('.h')
        
        # 写入文件
        with open(output, 'w', encoding='utf-8') as f:
            f.write(header_content)
        
        console.print(f"[green]✓ 成功生成头文件: {output}[/green]")
        
        # 打印生成汇总
        print_generation_summary(baud_rate, messages, rx_ids)
        
    except ValueError as e:
        console.print(f"[red]错误: {e}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]转换失败: {e}[/red]")
        import traceback
        traceback.print_exc()
        raise typer.Exit(code=1)


if __name__ == "__main__":
    # 使用app作为主入口 (支持多命令)
    app()
