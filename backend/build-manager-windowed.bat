@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0"

if exist ".venv\Scripts\activate.bat" (
  call ".venv\Scripts\activate.bat"
)

taskkill /F /IM "ResultBI BIMobile API Manager.exe" >nul 2>&1
taskkill /F /IM "ResultBI BIMobile API Manager" >nul 2>&1

for /f "delims=" %%i in ('python -c "import sys; print(sys.base_prefix)"') do set "PY_ROOT=%%i"
set "TCL_LIBRARY=%PY_ROOT%\tcl\tcl8.6"
set "TK_LIBRARY=%PY_ROOT%\tcl\tk8.6"

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

python -m PyInstaller ^
  --clean ^
  --onefile ^
  --windowed ^
  --name "ResultBI BIMobile API Manager" ^
  --collect-all tkinter ^
  --add-data "data;data" ^
  --add-data "app;app" ^
  --add-data "%TCL_LIBRARY%;tcl\tcl8.6" ^
  --add-data "%TK_LIBRARY%;tcl\tk8.6" ^
  --add-binary "%PY_ROOT%\DLLs\_tkinter.pyd;." ^
  --add-binary "%PY_ROOT%\DLLs\tcl86t.dll;." ^
  --add-binary "%PY_ROOT%\DLLs\tk86t.dll;." ^
  launcher\desktop_launcher.py

if not exist release mkdir release
if not exist release\data mkdir release\data
if not exist release\logs mkdir release\logs

copy /y "dist\ResultBI BIMobile API Manager.exe" "release\ResultBI BIMobile API Manager.exe"
copy /y "data\bases_config.json" "release\data\bases_config.json"
copy /y "data\permissions_config.json" "release\data\permissions_config.json"

echo Build windowed concluido em release\ResultBI BIMobile API Manager.exe
endlocal
