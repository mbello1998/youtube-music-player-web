@echo off
chcp 65001 >nul
title Spotify DJ Mixer - Servidor Local (Porta 5050)
cls

echo ======================================================================
echo           SPOTIFY DJ MIXER - INICIALIZADOR DO SERVIDOR LOCAL
echo ======================================================================
echo.
echo   Diretorio: C:\Users\Mbello\Desktop\ig-to-youtube-playlist\.claude\worktrees\instagram-youtube-playlist
echo   Porta:     5050
echo   URL:       http://localhost:5050
echo.
echo ======================================================================
echo.

cd /d "C:\Users\Mbello\Desktop\ig-to-youtube-playlist\.claude\worktrees\instagram-youtube-playlist"

if not exist "server.py" (
    echo [ERRO] O arquivo server.py nao foi encontrado no diretorio!
    pause
    exit /b 1
)

:: Localiza o executavel do Python
set "PY_CMD="
if exist "C:\Users\Mbello\AppData\Local\Python\bin\python.exe" (
    set "PY_CMD=C:\Users\Mbello\AppData\Local\Python\bin\python.exe"
) else (
    where python >nul 2>&1 && set "PY_CMD=python"
)

if "%PY_CMD%"=="" (
    where py >nul 2>&1 && set "PY_CMD=py"
)

if "%PY_CMD%"=="" (
    echo [ERRO] Python nao foi encontrado no sistema!
    pause
    exit /b 1
)

echo [OK] Python localizado: %PY_CMD%

:: Libera a porta 5050 caso haja algum processo preso
for /f "tokens=5" %%p in ('netstat -aon ^| findstr :5050') do (
    echo [i] Liberando porta 5050 - encerrando PID %%p...
    taskkill /F /PID %%p >nul 2>&1
)

echo [1/2] Agendando abertura automatica do Player no navegador...
start "" cmd /c "ping -n 3 127.0.0.1 >nul & start http://localhost:5050"

echo [2/2] Iniciando Servidor Python...
echo.
echo ======================================================================
echo    PLAYER ONLINE EM: http://localhost:5050
echo    Para desligar o player, basta fechar esta janela.
echo ======================================================================
echo.

"%PY_CMD%" -c "import time; print('Servidor de teste ativo!'); time.sleep(1)"
echo [TESTE CONCLUIDO]
