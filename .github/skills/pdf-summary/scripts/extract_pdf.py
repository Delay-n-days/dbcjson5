#!/usr/bin/env python
"""
PDF 文本和表格提取工具 (Typer 版本)
用于从 CAN 协议 PDF 文档中提取完整的文本和表格内容
适用于 summarize_pdf.py 失败的情况

支持多种输出格式和灵活的命令行选项
"""

from pathlib import Path

import pdfplumber
import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="PDF 文本和表格提取工具")
console = Console()


def find_pdf_file() -> Path | None:
    """查找当前目录中的第一个 PDF 文件"""
    pdf_files = list(Path('.').glob('*.pdf'))
    return pdf_files[0] if pdf_files else None


def extract_pdf_content(
    pdf_path: Path,
    output_file: Path | None = None,
    show_content: bool = True,
    show_stats: bool = True,
) -> bool:
    """
    从 PDF 提取所有文本和表格内容
    
    Args:
        pdf_path: PDF 文件路径
        output_file: 可选的输出文件路径
        show_content: 是否显示完整内容
        show_stats: 是否显示统计信息
    
    Returns:
        bool: 是否成功提取
    """
    pdf_file = Path(pdf_path)
    
    if not pdf_file.exists():
        console.print(f"[red]ERROR: 文件 {pdf_path} 不存在[/red]")
        return False
    
    output_lines = []
    
    try:
        with pdfplumber.open(str(pdf_file)) as pdf:
            total_pages = len(pdf.pages)
            
            msg = f"PDF 打开成功，共 {total_pages} 页"
            console.print(f"[green]OK {msg}[/green]\n")
            if output_file:
                output_lines.append(f"OK {msg}\n")
            
            # 统计信息
            total_text_chars = 0
            total_tables = 0
            
            # 逐页提取内容
            for page_num in range(total_pages):
                page = pdf.pages[page_num]
                text = page.extract_text()
                tables = page.extract_tables()
                
                if text:
                    total_text_chars += len(text)
                if tables:
                    total_tables += len(tables)
                
                if show_content:
                    # 页面分隔符
                    separator = "=" * 70
                    console.print(f"[bold blue]{separator}[/bold blue]")
                    console.print(f"[bold blue]第 {page_num + 1} 页[/bold blue]")
                    console.print(f"[bold blue]{separator}[/bold blue]")
                    
                    if output_file:
                        output_lines.append(f"\n{separator}")
                        output_lines.append(f"第 {page_num + 1} 页")
                        output_lines.append(f"{separator}")
                    
                    # 文本内容
                    if text:
                        console.print("\n[cyan]【文本内容】[/cyan]")
                        console.print(text)
                        if output_file:
                            output_lines.append("\n【文本内容】")
                            output_lines.append(text)
                    else:
                        console.print("\n[yellow]【文本内容】(空页)[/yellow]")
                        if output_file:
                            output_lines.append("\n【文本内容】(空页)")
                    
                    # 表格内容
                    if tables:
                        console.print(f"\n[yellow]【找到 {len(tables)} 个表格】[/yellow]")
                        if output_file:
                            output_lines.append(f"\n【找到 {len(tables)} 个表格】")
                        
                        for table_num, table in enumerate(tables, 1):
                            console.print(f"\n[yellow]--- 表格 {table_num} ---[/yellow]")
                            if output_file:
                                output_lines.append(f"\n--- 表格 {table_num} ---")
                            
                            for row_num, row in enumerate(table):
                                row_str = f"行 {row_num + 1}: {row}"
                                console.print(row_str)
                                if output_file:
                                    output_lines.append(row_str)
                    
                    console.print()  # 空行分隔
                    if output_file:
                        output_lines.append("")
            
            # 显示统计信息
            if show_stats:
                console.print(f"\n[bold green]{'='*70}[/bold green]")
                console.print("[bold green]提取统计[/bold green]")
                console.print(f"[bold green]{'='*70}[/bold green]")
                
                stats_table = Table(show_header=True, header_style="bold")
                stats_table.add_column("指标", style="cyan")
                stats_table.add_column("值", style="magenta")
                
                stats_table.add_row("总页数", str(total_pages))
                stats_table.add_row("总文本字符数", str(total_text_chars))
                stats_table.add_row("总表格数", str(total_tables))
                
                console.print(stats_table)
                
                if output_file:
                    output_lines.append(f"\n{'='*70}")
                    output_lines.append("提取统计")
                    output_lines.append(f"{'='*70}")
                    output_lines.append(f"总页数: {total_pages}")
                    output_lines.append(f"总文本字符数: {total_text_chars}")
                    output_lines.append(f"总表格数: {total_tables}")
            
            console.print(f"\n[green]✓ 提取完成！共 {total_pages} 页[/green]")
            
            # 保存到文件
            if output_file:
                output_file.parent.mkdir(parents=True, exist_ok=True)
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(output_lines))
                console.print(f"[green]✓ 结果已保存到: {output_file}[/green]")
            
            return True
            
    except (OSError, RuntimeError) as e:
        console.print(f"[red]ERROR: 提取失败: {e}[/red]")
        import traceback
        traceback.print_exc()
        return False


@app.command()
def extract(
    pdf_path: str | None = typer.Argument(
        None,
        help="PDF 文件路径（可选，不指定则自动查找）"
    ),
    output: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="输出文件路径（可选）"
    ),
    no_content: bool = typer.Option(
        False,
        "--no-content",
        help="隐藏完整文档内容，仅显示统计"
    ),
    no_stats: bool = typer.Option(
        False,
        "--no-stats",
        help="隐藏统计信息"
    ),
):
    """提取 PDF 文本和表格内容"""
    
    # 确定 PDF 文件路径
    if pdf_path:
        pdf_file = Path(pdf_path)
    else:
        pdf_file = find_pdf_file()
        if not pdf_file:
            console.print("[red]ERROR: 未找到 PDF 文件[/red]")
            console.print("[yellow]Usage: python extract_pdf.py <pdf-filepath>[/yellow]")
            raise typer.Exit(code=1)
        console.print(f"[yellow]未指定 PDF，使用找到的第一个文件: {pdf_file}[/yellow]\n")
    
    # 执行提取
    success = extract_pdf_content(
        pdf_file,
        output_file=output,
        show_content=not no_content,
        show_stats=not no_stats,
    )
    
    raise typer.Exit(code=0 if success else 1)


if __name__ == '__main__':
    app()
