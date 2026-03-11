#!/usr/bin/env python3
"""
提取并总结 GTAKE 扩展帧通讯协议 PDF 文件
CLI 应用使用 Typer 框架
"""

from pathlib import Path
from typing import Optional
import typer
import pdfplumber

app = typer.Typer(
    name="PDF Summary Tool",
    help="Extract and summarize CAN protocol PDF documents",
)

def print_separator(char: str = "=") -> None:
    """打印分隔线"""
    typer.echo(char * 70)

@app.command()
def summarize(
    pdf_path: str = typer.Argument(
        ...,
        help="Path to PDF file to summarize",
        show_default=False,
    ),
    output_file: Optional[str] = typer.Option(
        None,
        "--output",
        "-o",
        help="Save output to file (optional)",
    ),
    show_content: bool = typer.Option(
        True,
        "--content/--no-content",
        help="Show full document content",
    ),
    show_stats: bool = typer.Option(
        True,
        "--stats/--no-stats",
        help="Show statistics",
    ),
    keywords: Optional[str] = typer.Option(
        None,
        "--keywords",
        "-k",
        help="Custom keywords to search (comma-separated)",
    ),
) -> None:
    """Extract and summarize PDF document"""
    
    pdf_file = Path(pdf_path).resolve()
    
    if not pdf_file.exists():
        typer.secho(f"ERROR: File not found: {pdf_path}", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    
    if not pdf_file.suffix.lower() == ".pdf":
        typer.secho(f"ERROR: File is not a PDF: {pdf_file.suffix}", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    
    typer.secho(f"Processing: {pdf_file.name}", fg=typer.colors.CYAN, bold=True)
    print_separator()
    
    try:
        with pdfplumber.open(str(pdf_file)) as pdf:
            total_pages = len(pdf.pages)
            typer.echo(f"\nTotal Pages: {total_pages}")
            
            # 提取全部文本
            full_text = ""
            for i, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if text:
                    full_text += f"\n--- PAGE {i} ---\n{text}"
            
            # 输出内容
            if show_content:
                typer.echo("\n[DOCUMENT CONTENT]\n")
                typer.echo(full_text)
            
            # 输出统计信息
            if show_stats:
                print_separator()
                typer.secho("\n[STATISTICS]", fg=typer.colors.GREEN)
                typer.echo(f"Total text length: {len(full_text)} characters")
                typer.echo(f"Total pages: {total_pages}")
                
                # 关键词检测
                search_keywords = [
                    "报文", "信号", "ID", "长度", "周期",
                    "波特率", "CAN", "扩展帧"
                ]
                
                # 如果用户提供了自定义关键词
                if keywords:
                    search_keywords.extend([kw.strip() for kw in keywords.split(",")])
                
                typer.secho("\n[KEYWORDS]", fg=typer.colors.YELLOW)
                for kw in search_keywords:
                    count = full_text.count(kw)
                    if count > 0:
                        typer.echo(f"  '{kw}': {count} times")
            
            # 保存到文件（如果指定了输出文件）
            if output_file:
                output_path = Path(output_file)
                output_path.write_text(full_text, encoding="utf-8")
                typer.secho(
                    f"\nOutput saved to: {output_path.absolute()}",
                    fg=typer.colors.GREEN,
                )
    
    except Exception as e:
        typer.secho(f"ERROR: {str(e)}", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    
    typer.secho("\nCompleted successfully!", fg=typer.colors.GREEN)

@app.command()
def extract_text(
    pdf_path: str = typer.Argument(
        ...,
        help="Path to PDF file",
        show_default=False,
    ),
    output_file: str = typer.Option(
        ...,
        "--output",
        "-o",
        help="Save extracted text to file",
    ),
) -> None:
    """Extract plain text from PDF and save to file"""
    
    pdf_file = Path(pdf_path).resolve()
    output_path = Path(output_file)
    
    if not pdf_file.exists():
        typer.secho(f"ERROR: File not found: {pdf_path}", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    
    typer.secho(f"Extracting text from: {pdf_file.name}", fg=typer.colors.CYAN)
    
    try:
        with pdfplumber.open(str(pdf_file)) as pdf:
            text = ""
            for i, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text += f"--- PAGE {i} ---\n{page_text}\n\n"
            
            output_path.write_text(text, encoding="utf-8")
            typer.secho(
                f"Text extracted to: {output_path.absolute()}",
                fg=typer.colors.GREEN,
            )
    
    except Exception as e:
        typer.secho(f"ERROR: {str(e)}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
