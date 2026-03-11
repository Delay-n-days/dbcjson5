#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pdfplumber
import json

pdf_path = '绿控传动TMCU通讯协议1C.pdf'

try:
    with pdfplumber.open(pdf_path) as pdf:
        print(f'PDF 页数: {len(pdf.pages)}')
        
        # 提取前10页的文本和表格信息
        for i in range(min(10, len(pdf.pages))):
            page = pdf.pages[i]
            text = page.extract_text()
            tables = page.extract_tables()
            
            print(f'\n{"="*60}')
            print(f'第 {i+1} 页')
            print(f'{"="*60}')
            
            if text:
                print('文本内容（前1000字）:')
                print(text[:1000])
            
            if tables:
                print(f'\n找到 {len(tables)} 个表格')
                for j, table in enumerate(tables):
                    print(f'\n表格 {j+1}:')
                    for row in table[:5]:  # 显示前5行
                        print(row)
            
except Exception as e:
    print(f'错误: {e}')
