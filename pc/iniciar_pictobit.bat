@echo off
title Picto:Bit
rem Arranca Picto:Bit desde la carpeta donde esta este archivo
cd /d "%~dp0"
py -3.13 picto_bit.py
if errorlevel 1 (
    echo.
    echo Ha ocurrido un error. Lee el mensaje de arriba.
    pause
)
