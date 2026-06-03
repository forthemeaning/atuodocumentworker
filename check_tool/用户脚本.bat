@echo off
chcp 65001 >nul
cd /d "%~dp0"
python user_check.py
pause