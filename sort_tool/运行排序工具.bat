@echo off
chcp 65001 >nul
cd /d "%~dp0"
python sort_main.py
pause