@echo off
REM csv2dbc - Windows 批处理启动脚本
REM 
REM 用法:
REM   csv2dbc.bat convert "data.csv"
REM   csv2dbc.bat convert "data.csv" -o output.dbc -e utf-8
REM   csv2dbc.bat --help
REM   csv2dbc.bat version

setlocal enabledelayedexpansion

REM 获取脚本所在目录
for %%i in ("%~dp0.") do set "SCRIPT_DIR=%%~fi"

REM 调用 Python 脚本
python "%SCRIPT_DIR%\csv2dbc.py" %*

REM 保留返回代码
exit /b %errorlevel%
