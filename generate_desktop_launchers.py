bat_path = r"C:\Users\Mbello\Desktop\Iniciar_Player.bat"
vbs_path = r"C:\Users\Mbello\Desktop\Iniciar_Player_Silencioso.vbs"

bat_code = """@echo off
chcp 65001 >nul
title Spotify DJ Mixer - Servidor Local (Porta 5050)
cls

echo ======================================================================
echo           SPOTIFY DJ MIXER - INICIALIZADOR DO SERVIDOR LOCAL
echo ======================================================================
echo.
echo   Diretorio: C:\\Users\\Mbello\\Desktop\\ig-to-youtube-playlist\\.claude\\worktrees\\instagram-youtube-playlist
echo   Porta:     5050
echo   URL:       http://localhost:5050
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

echo [OK] Python localizado: %PY_CMD%

:: Libera a porta 5050 caso haja algum processo preso ocupando
for /f "tokens=5" %%p in ('netstat -aon ^| findstr :5050') do (
    echo [i] Liberando porta 5050 - encerrando PID %%p...
    taskkill /F /PID %%p >nul 2>&1
)

:: Agenda a abertura do navegador apos 2 segundos (tempo para o servidor subir)
echo [1/2] Agendando abertura automatica do Player no navegador...
start "" cmd /c "ping -n 3 127.0.0.1 >nul & start http://localhost:5050"

echo [2/2] Iniciando Servidor Python na porta 5050...
echo.
echo ======================================================================
echo    PLAYER ONLINE EM: http://localhost:5050
echo    Para desligar o player e o servidor, basta fechar esta janela.
echo ======================================================================
echo.

"%PY_CMD%" -u server.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [AVISO] Servidor encerrou com codigo de erro %ERRORLEVEL%.
    pause
)
"""

crlf_bat = bat_code.replace("\r\n", "\n").replace("\n", "\r\n")
with open(bat_path, "wb") as f:
    f.write(crlf_bat.encode("utf-8"))
print("Gravado com sucesso:", bat_path)

vbs_code = """Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

serverDir = "C:\\Users\\Mbello\\Desktop\\ig-to-youtube-playlist\\.claude\\worktrees\\instagram-youtube-playlist"
serverScript = serverDir & "\\server.py"
WshShell.CurrentDirectory = serverDir

pythonExe = "C:\\Users\\Mbello\\AppData\\Local\\Python\\bin\\python.exe"
If Not fso.FileExists(pythonExe) Then
    pythonExe = "python.exe"
End If

Set objExec = WshShell.Exec("cmd /c netstat -aon | findstr :5050")
strOutput = objExec.StdOut.ReadAll

If InStr(strOutput, "LISTENING") > 0 Then
    WshShell.Run "cmd /c for /f ""tokens=5"" %p in ('netstat -aon ^| findstr :5050') do taskkill /F /PID %p", 0, True
    WScript.Sleep 1000
End If

WshShell.Run Chr(34) & pythonExe & Chr(34) & " -u " & Chr(34) & serverScript & Chr(34), 0, False
WScript.Sleep 1500

WshShell.Run "http://localhost:5050"
"""

crlf_vbs = vbs_code.replace("\r\n", "\n").replace("\n", "\r\n")
with open(vbs_path, "wb") as f:
    f.write(crlf_vbs.encode("utf-8"))
print("Gravado com sucesso:", vbs_path)
