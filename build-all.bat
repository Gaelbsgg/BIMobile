@echo off
setlocal enabledelayedexpansion

set "ROOT=%~dp0"
set "BACKEND=%ROOT%backend"
set "RELEASE=%ROOT%release\BIMobile"
set "PYTHON=%BACKEND%\.venv\Scripts\python.exe"

if not exist "%PYTHON%" (
  set "PYTHON=python"
)

if not exist "%BACKEND%\bin\config.json" (
  echo config.json base nao encontrado em "%BACKEND%\bin\config.json".
  exit /b 1
)

if exist "%BACKEND%\build_api" rmdir /s /q "%BACKEND%\build_api"
if exist "%BACKEND%\build_manager" rmdir /s /q "%BACKEND%\build_manager"
if exist "%BACKEND%\dist_api" rmdir /s /q "%BACKEND%\dist_api"
if exist "%BACKEND%\dist_manager" rmdir /s /q "%BACKEND%\dist_manager"
if exist "%RELEASE%" rmdir /s /q "%RELEASE%"

mkdir "%RELEASE%\bin" >nul 2>&1
mkdir "%RELEASE%\data" >nul 2>&1
mkdir "%RELEASE%\logs" >nul 2>&1

"%PYTHON%" -m pip install --upgrade pip
"%PYTHON%" -m pip install -r "%BACKEND%\requirements.txt"
"%PYTHON%" -m pip install pyinstaller

"%PYTHON%" -m PyInstaller ^
  --clean ^
  --noconfirm ^
  --onefile ^
  --windowed ^
  --name "BIMobileAPI" ^
  --distpath "%BACKEND%\dist_api" ^
  --workpath "%BACKEND%\build_api" ^
  --specpath "%BACKEND%\build_api" ^
  --hidden-import firebird.driver ^
  --hidden-import fdb ^
  --add-data "%BACKEND%\data;data" ^
  "%BACKEND%\api_entry.py"

"%PYTHON%" -m PyInstaller ^
  --clean ^
  --noconfirm ^
  --onefile ^
  --windowed ^
  --name "BIMobileManager" ^
  --distpath "%BACKEND%\dist_manager" ^
  --workpath "%BACKEND%\build_manager" ^
  --specpath "%BACKEND%\build_manager" ^
  --collect-all tkinter ^
  --collect-all pystray ^
  --hidden-import firebird.driver ^
  --hidden-import fdb ^
  --add-data "%BACKEND%\data;data" ^
  --icon "%BACKEND%\bin\resultbi.ico" ^
  "%BACKEND%\launcher\desktop_launcher.py"

copy /y "%BACKEND%\dist_api\BIMobileAPI.exe" "%RELEASE%\bin\BIMobileAPI.exe"
copy /y "%BACKEND%\dist_manager\BIMobileManager.exe" "%RELEASE%\bin\BIMobileManager.exe"
copy /y "%BACKEND%\bin\config.json" "%RELEASE%\bin\config.json"

if exist "%BACKEND%\bin\resultbi.ico" (
  copy /y "%BACKEND%\bin\resultbi.ico" "%RELEASE%\bin\resultbi.ico"
)

if exist "%BACKEND%\bin\nssm.exe" (
  copy /y "%BACKEND%\bin\nssm.exe" "%RELEASE%\bin\nssm.exe"
)

if exist "%BACKEND%\bin\cloudflared.exe" (
  copy /y "%BACKEND%\bin\cloudflared.exe" "%RELEASE%\bin\cloudflared.exe"
)

copy /y "%BACKEND%\data\bases_config.json" "%RELEASE%\data\bases_config.json"
copy /y "%BACKEND%\data\permissions_config.json" "%RELEASE%\data\permissions_config.json"

copy /y "%ROOT%install-service.bat" "%RELEASE%\install-service.bat"
copy /y "%ROOT%uninstall-service.bat" "%RELEASE%\uninstall-service.bat"
copy /y "%ROOT%start-service.bat" "%RELEASE%\start-service.bat"
copy /y "%ROOT%stop-service.bat" "%RELEASE%\stop-service.bat"
copy /y "%ROOT%open-manager.bat" "%RELEASE%\open-manager.bat"

echo Build concluido em "%RELEASE%".
endlocal
