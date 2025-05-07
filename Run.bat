@echo off
cd /d %~dp0
call activate AICoachServer
python Main.py
cmd /k