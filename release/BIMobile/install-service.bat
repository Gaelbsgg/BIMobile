@echo off
setlocal

set "ROOT=%~dp0"
set "BIN=%ROOT%bin"
set "NSSM=%BIN%\nssm.exe"
set "SERVICE=BIMobileAPI"
set "API_EXE=%BIN%\BIMobileAPI.exe"
set "LOG_DIR=%ROOT%logs"

if not exist "%NSSM%" (
  echo nssm.exe nao encontrado em "%NSSM%".
  exit /b 1
)

if not exist "%API_EXE%" (
  echo BIMobileAPI.exe nao encontrado em "%API_EXE%".
  exit /b 1
)

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

"%NSSM%" stop "%SERVICE%" >nul 2>&1
"%NSSM%" remove "%SERVICE%" confirm >nul 2>&1
"%NSSM%" install "%SERVICE%" "%API_EXE%"
"%NSSM%" set "%SERVICE%" AppDirectory "%BIN%"
"%NSSM%" set "%SERVICE%" AppStdout "%LOG_DIR%\BIMobileAPI.out.log"
"%NSSM%" set "%SERVICE%" AppStderr "%LOG_DIR%\BIMobileAPI.err.log"
"%NSSM%" set "%SERVICE%" AppRotateFiles 1
"%NSSM%" set "%SERVICE%" Start SERVICE_AUTO_START
"%NSSM%" start "%SERVICE%"

echo Servico %SERVICE% instalado e iniciado.
endlocal
