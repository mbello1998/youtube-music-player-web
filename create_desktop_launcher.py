import os

bat_path = r"C:\Users\Mbello\Desktop\Iniciar_Player.bat"
vbs_path = r"C:\Users\Mbello\Desktop\Iniciar_Player_Silencioso.vbs"

bat_content = """@echo off
chcp 65001 >nul
title Spotify DJ Mixer - Servidor Local (Porta 5050)
cls
color 0B

echo ======================================================================
echo           SPOTIFY DJ MIXER - INICIALIZADOR DO SERVIDOR LOCAL
echo ======================================================================
echo.
echo   [+] Diretorio: C:\\Users\\Mbello\\Desktop\\ig-to-youtube-playlist\\.claude\\worktrees\\instagram-youtube-playlist
echo   [+] Porta:     5050
echo   [+] URL:       http://localhost:5050
echo.
echo ======================================================================
echo.

cd /d "C:\\Users\\Mbello\\Desktop\\ig-to-youtube-playlist\\.claude\\worktrees\\instagram-youtube-playlist"

if not exist "server.py" (
    echo [ERRO] O arquivo server.py nao foi encontrado no diretorio!
    pause
    exit /b 1
)

:: Localiza o executavel do Python
set "PY_CMD="
if exist "C:\\Users\\Mbello\\AppData\\Local\\Python\\bin\\python.exe" (
    set "PY_CMD=C:\\Users\\Mbello\\AppData\\Local\\Python\\bin\\python.exe"
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

:: Libera a porta 5050 caso haja algum processo preso ocupando
for /f "tokens=5" %%p in ('netstat -aon ^| findstr /R /C:"TCP.*:5050 .*LISTENING"') do (
    echo [i] Liberando porta 5050 (encerrando processo anterior PID %%p)...
    taskkill /F /PID %%p >nul 2>&1
)
ping -n 2 127.0.0.1 >nul

:: Agenda a abertura do navegador assim que o servidor inicializar
echo [1/2] Agendando abertura automatica do Player no navegador...
start "" cmd /c "ping -n 3 127.0.0.1 >nul & start http://localhost:5050"

echo [2/2] Iniciando Servidor Python na porta 5050...
echo.
echo ======================================================================
echo    PLAYER ONLINE EM: http://localhost:5050
echo    Para desligar o player, basta fechar esta janela.
echo ======================================================================
echo.

"%PY_CMD%" -u server.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [AVISO] Servidor encerrou com codigo de erro %ERRORLEVEL%.
    pause
)
"""

crlf_bat = bat_content.replace("\r\n", "\n").replace("\n", "\r\n")

with open(bat_path, "wb") as f:
    f.write(crlf_bat.encode("utf-8"))

print(f"Arquivo BAT gravado com CRLF em: {bat_path} ({len(crlf_bat)} bytes)")

vbs_lines = [
    'Set WshShell = CreateObject("WScript.Shell")',
    'Set fso = CreateObject("Scripting.FileSystemObject")',
    '',
    r'serverDir = "C:\Users\Mbello\Desktop\ig-to-youtube-playlist\.claude\worktrees\instagram-youtube-playlist"',
    'WshShell.CurrentDirectory = serverDir',
    '',
    r'pythonExe = "C:\Users\Mbello\AppData\Local\Python\bin\python.exe"',
    'If Not fso.FileExists(pythonExe) Then',
    '    pythonExe = "python.exe"',
    'End If',
    '',
    'Set objExec = WshShell.Exec("cmd /c netstat -aon | findstr :5050")',
    'strOutput = objExec.StdOut.ReadAll',
    '',
    'If InStr(strOutput, "LISTENING") > 0 Then',
    r'    WshShell.Run "cmd /c for /f ""tokens=5"" %p in (\'netstat -aon ^| findstr /R /C:""TCP.*:5050 .*LISTENING""\') do taskkill /F /PID %p", 0, True',
    '    WScript.Sleep 1000',
    'End If',
    '',
    'WshShell.Run Chr(34) & pythonExe & Chr(34) & " -u server.py", 0, False',
    'WScript.Sleep 1500',
    '',
    'WshShell.Run "http://localhost:5050"',
]

crlf_vbs = "\r\n".join(vbs_lines) + "\r\n"
with open(vbs_path, "wb") as f:
    f.write(crlf_vbs.encode("utf-8"))

print(f"Arquivo VBS gravado com CRLF em: {vbs_path} ({len(crlf_vbs)} bytes)")
