@echo off
chcp 65001 >nul
title Apresentacao Pericial - Servidor Local
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py servir_apresentacao.py
) else (
  python servir_apresentacao.py
)
if errorlevel 1 pause
