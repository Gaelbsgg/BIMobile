@echo off
setlocal

set "ROOT=%~dp0"
set "BIN=%ROOT%bin"
set "NSSM=%BIN%\nssm.exe"
set "SERVICE=BIMobileAPI"

if not exist "%NSSM%" (
  echo nssm.exe nao encontrado em "%NSSM%".
  exit /b 1
)

"%NSSM%" stop "%SERVICE%"
endlocal
