#!/usr/bin/env python3
"""
Excel文件分析工具
读取Excel文件并显示所有工作表和内容
"""

import argparse
import sys
from pathlib import Path

import pandas as pd
from rich.console import Console
from rich.table import Table as RichTable

console = Console()


def analyze_excel(excel_path: Path, output_path: Path | None = None) -> None:
    """
    分析Excel文件，显示所有工作表内容
    
    Args:
        excel_path: Excel文件路径
        output_path: 输出文本文件路径（可选）
    """
    try:
        # 读取所有工作表
        df_dict = pd.read_excel(excel_path, sheet_name=None)
    except Exception as e:
        console.print(f"[red]❌ 无法打开Excel文件: {e}[/red]")
        return
    
    console.print(f"[green]✓ Excel文件打开成功: {excel_path.name}[/green]")
    console.print(f"[cyan]工作表数量: {len(df_dict)}[/cyan]\n")
    
    content_lines = []
    content_lines.append(f"Excel文件: {excel_path.name}")
    content_lines.append("=" * 80)
    content_lines.append("")
    
    # 遍历所有工作表
    for sheet_idx, (sheet_name, df) in enumerate(df_dict.items(), 1):
        console.print(f"[bold cyan]工作表 {sheet_idx}: {sheet_name}[/bold cyan]")
        console.print(f"  行数: {len(df)}, 列数: {len(df.columns)}")
        
        content_lines.append("")
        content_lines.append(f"{'=' * 80}")
        content_lines.append(f"工作表 {sheet_idx}: {sheet_name}")
        content_lines.append(f"行数: {len(df)}, 列数: {len(df.columns)}")
        content_lines.append(f"{'=' * 80}")
        content_lines.append("")
        
        # 显示列名
        console.print(f"  列名: {', '.join(str(col) for col in df.columns)}\n")
        content_lines.append(f"列名: {', '.join(str(col) for col in df.columns)}")
        content_lines.append("")
        
        # 显示数据
        # 使用Rich Table显示前几行
        if len(df) > 0:
            display_rows = min(10, len(df))
            table = RichTable(title=f"{sheet_name} (前{display_rows}行)")
            
            # 添加列
            for col in df.columns:
                table.add_column(str(col), style="cyan", no_wrap=False)
            
            # 添加行
            for idx, row in df.head(display_rows).iterrows():
                table.add_row(*[str(val) if pd.notna(val) else "" for val in row])
            
            console.print(table)
            console.print("")
        
        # 写入完整数据到文本文件
        content_lines.append("数据内容:")
        content_lines.append("-" * 80)
        
        # 添加表头
        header = " | ".join(str(col) for col in df.columns)
        content_lines.append(header)
        content_lines.append("-" * 80)
        
        # 添加所有行
        for idx, row in df.iterrows():
            row_str = " | ".join(str(val) if pd.notna(val) else "" for val in row)
            content_lines.append(f"行{idx + 1}: {row_str}")
        
        content_lines.append("")
    
    # 保存到文件
    if output_path:
        full_content = "\n".join(content_lines)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(full_content, encoding='utf-8')
        console.print(f"[green]✓ 分析完成！[/green]")
        console.print(f"[green]✓ 结果已保存到: {output_path}[/green]")


def main():
    parser = argparse.ArgumentParser(
        description="分析Excel文件内容",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 分析Excel文件
  python analyze_excel.py protocol.xlsx
  
  # 保存分析结果
  python analyze_excel.py protocol.xlsx -o analysis.txt
  
  # 使用uv运行
  uv run python analyze_excel.py protocol.xlsx -o analysis.txt
        """
    )
    
    parser.add_argument(
        'excel_file',
        type=Path,
        help='要分析的Excel文件路径'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=Path,
        default=None,
        help='输出文本文件路径（可选）'
    )
    
    args = parser.parse_args()
    
    # 检查输入文件是否存在
    if not args.excel_file.exists():
        console.print(f"[red]❌ 文件不存在: {args.excel_file}[/red]")
        return 1
    
    # 确定输出路径
    if args.output is None:
        args.output = args.excel_file.with_suffix('.txt')
    
    try:
        analyze_excel(args.excel_file, args.output)
        return 0
    except Exception as e:
        console.print(f"[red]❌ 分析失败: {e}[/red]")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
