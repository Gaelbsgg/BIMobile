@echo off
setlocal

set "ROOT=%~dp0"
set "BIN=%ROOT%bin"
set "MANAGER=%BIN%\BIMobileManager.exe"

if not exist "%MANAGER%" (
  echo BIMobileManager.exe nao encontrado em "%MANAGER%".
  exit /b 1
)

start "" "%MANAGER%"
endlocal
