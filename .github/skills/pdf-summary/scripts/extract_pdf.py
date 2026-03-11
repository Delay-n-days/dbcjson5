#!/usr/bin/env python
"""
PDF 文本和表格提取工具
用于从 CAN 协议 PDF 文档中提取完整的文本和表格内容
适用于 summarize_pdf.py 失败的情况
"""

import sys
from pathlib import Path

import pdfplumber


def extract_pdf_content(pdf_path):
    """
    从 PDF 提取所有文本和表格内容
    
    Args:
        pdf_path: PDF 文件路径
    
    Returns:
        bool: 是否成功提取
    """
    pdf_file = Path(pdf_path)
    
    if not pdf_file.exists():
        print(f"❌ 错误: 文件 {pdf_path} 不存在")
        return False
    
    try:
        with pdfplumber.open(str(pdf_file)) as pdf:
            total_pages = len(pdf.pages)
            print(f"✓ PDF 打开成功，共 {total_pages} 页\n")
            
            # 逐页提取内容
            for page_num in range(total_pages):
                page = pdf.pages[page_num]
                text = page.extract_text()
                tables = page.extract_tables()
                
                # 页面分隔符
                print(f"{'='*70}")
                print(f"第 {page_num + 1} 页")
                print(f"{'='*70}")
                
                # 文本内容
                if text:
                    print("\n【文本内容】")
                    print(text)
                else:
                    print("\n【文本内容】(空页)")
                
                # 表格内容
                if tables:
                    print(f"\n【找到 {len(tables)} 个表格】")
                    for table_num, table in enumerate(tables, 1):
                        print(f"\n--- 表格 {table_num} ---")
                        for row_num, row in enumerate(table):
                            print(f"行 {row_num + 1}: {row}")
                
                print()  # 空行分隔
            
            print(f"\n{'='*70}")
            print(f"✓ 提取完成！共 {total_pages} 页")
            print(f"{'='*70}\n")
            
            return True
            
    except (OSError, RuntimeError) as e:
        print(f"❌ 提取失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    # 获取 PDF 文件路径
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        # 查找当前目录中的第一个 PDF 文件
        pdf_files = list(Path('.').glob('*.pdf'))
        if pdf_files:
            pdf_path = str(pdf_files[0])
            print(f"未指定 PDF，使用找到的第一个文件: {pdf_path}\n")
        else:
            print("❌ 错误: 未找到 PDF 文件")
            print("用法: python extract_pdf.py <pdf文件路径>")
            return 1
    
    # 提取内容
    success = extract_pdf_content(pdf_path)
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
