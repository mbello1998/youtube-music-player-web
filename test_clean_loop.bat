@echo off
set "FOUND="
for /f "tokens=5" %%p in ('netstat -aon ^| findstr :5050') do (
    echo Encontrado PID %%p
    set "FOUND=1"
)
if "%FOUND%"=="" echo Nenhum processo na porta 5050.
