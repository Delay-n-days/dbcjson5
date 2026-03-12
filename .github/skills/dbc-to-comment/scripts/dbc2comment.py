#!/usr/bin/env python3
"""
DBC to C Comment JSON Generator
从 DBC 文件提取信号信息，生成 C 语言注释格式的 JSON 文件
"""

import json
import cantools
from pathlib import Path
from typing import List, Dict, Any
import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="DBC 到 C 注释 JSON 转换工具")
console = Console()


def generate_signal_comment(
    signal_name: str,
    start_bit: int,
    length: int,
    scale: float,
    offset: float,
    unit: str,
    description: str
) -> str:
    """
    生成 C 语言风格的信号注释
    
    Args:
        signal_name: 信号名称
        start_bit: 起始位
        length: 长度（位）
        scale: 系数
        offset: 偏移量
        unit: 单位
        description: 描述信息
    
    Returns:
        格式化的注释字符串
    """
    # 构建注释各部分
    parts = [
        f"// {signal_name}",
        f"起始位:{start_bit}",
        f"长度:{length}",
        f"系数:{scale}",
        f"偏移量:{offset}"
    ]
    
    # 如果有单位，添加单位
    if unit:
        parts.append(f"单位:{unit}")
    
    # 如果有描述信息，添加到最后
    if description:
        # 处理多行描述，每行都添加 // 前缀
        desc_lines = description.split('\n')
        if len(desc_lines) > 1:
            # 第一行跟在主注释后面
            parts.append(desc_lines[0])
            # 后续行单独成行，每行加 // 前缀
            for line in desc_lines[1:]:
                parts.append(f"\n// {line}")
        else:
            parts.append(description)
    
    return "\t".join(parts)


def extract_signal_info(db: cantools.database.Database) -> List[Dict[str, str]]:
    """
    从 DBC 数据库中提取所有信号信息
    
    Args:
        db: cantools 数据库对象
    
    Returns:
        信号字典列表，每个字典包含信号名称和注释
    """
    signals_info = []
    
    for message in db.messages:
        for signal in message.signals:
            # 获取信号的基本信息
            signal_name = signal.name
            start_bit = signal.start
            length = signal.length
            scale = signal.scale if signal.scale else 1
            offset = signal.offset if signal.offset else 0
            unit = signal.unit if signal.unit else ""
            
            # 获取描述信息
            description = ""
            if signal.comment:
                # 如果注释中包含 JSON 格式的枚举或描述
                comment_text = signal.comment.strip()
                
                # 尝试解析 JSON
                try:
                    comment_json = json.loads(comment_text)
                    if isinstance(comment_json, dict):
                        # 如果是枚举值
                        if "description" in comment_json:
                            description = comment_json["description"]
                        else:
                            # 枚举值格式
                            enum_parts = [f"{k}:{v}" for k, v in comment_json.items()]
                            description = " ".join(enum_parts)
                except json.JSONDecodeError:
                    # 如果不是 JSON，直接使用注释文本
                    description = comment_text
            
            # 生成注释
            comment = generate_signal_comment(
                signal_name, start_bit, length, scale, offset, unit, description
            )
            
            # 添加到列表
            signals_info.append({signal_name: comment})
    
    return signals_info


@app.command()
def convert(
    dbc_file: str = typer.Argument(..., help="输入的 DBC 文件路径"),
    output: str = typer.Option(
        None, "-o", "--output", help="输出的 JSON 文件路径（默认与 DBC 同名）"
    ),
    encoding: str = typer.Option(
        "utf-8", "-e", "--encoding", help="DBC 文件编码"
    ),
    indent: int = typer.Option(
        4, "-i", "--indent", help="JSON 缩进空格数"
    ),
    show_preview: bool = typer.Option(
        True, "-p", "--preview", help="显示前 10 条信号预览"
    )
):
    """
    从 DBC 文件生成 C 语言注释 JSON 文件
    
    示例:
        python dbc2comment.py convert GTAKE_motor_250K.dbc
        python dbc2comment.py convert GTAKE_motor_250K.dbc -o comments.json
    """
    try:
        # 确认输入文件存在
        dbc_path = Path(dbc_file)
        if not dbc_path.exists():
            console.print(f"[red]✗ 文件不存在: {dbc_file}[/red]")
            raise typer.Exit(code=1)
        
        # 确定输出文件路径
        if output is None:
            output_path = dbc_path.with_name(f"{dbc_path.stem}_comment.json")
        else:
            output_path = Path(output)
        
        console.print(f"[cyan]正在读取 DBC 文件: {dbc_file}[/cyan]")
        
        # 读取 DBC 文件
        try:
            db = cantools.database.load_file(dbc_file, encoding=encoding)
        except Exception as e:
            console.print(f"[red]✗ 读取 DBC 文件失败: {e}[/red]")
            raise typer.Exit(code=1)
        
        # 提取信号信息
        console.print("[cyan]正在提取信号信息...[/cyan]")
        signals_info = extract_signal_info(db)
        
        # 显示统计
        console.print(f"[green]✓ 消息数量: {len(db.messages)}[/green]")
        console.print(f"[green]✓ 信号数量: {len(signals_info)}[/green]")
        
        # 显示预览
        if show_preview and signals_info:
            table = Table(title="信号预览（前 10 条）", show_lines=True)
            table.add_column("信号名称", style="cyan", no_wrap=True)
            table.add_column("注释", style="white")
            
            for item in signals_info[:10]:
                for name, comment in item.items():
                    # 截断过长的注释
                    display_comment = comment if len(comment) <= 100 else comment[:97] + "..."
                    table.add_row(name, display_comment)
            
            console.print(table)
        
        # 写入 JSON 文件
        console.print(f"[cyan]正在写入 JSON 文件: {output_path}[/cyan]")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(signals_info, f, ensure_ascii=False, indent=indent)
        
        console.print(f"[green]✓ 输出文件: {output_path}[/green]")
        console.print(f"[green]✓ 成功生成 {len(signals_info)} 条信号注释[/green]")
        
    except Exception as e:
        console.print(f"[red]✗ 错误: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def version():
    """显示版本信息"""
    console.print("DBC to C Comment JSON Generator v1.0.0")
    console.print("使用 cantools 库解析 DBC 文件")


if __name__ == "__main__":
    app()
