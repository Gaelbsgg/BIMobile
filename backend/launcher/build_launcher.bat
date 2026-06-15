@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0\.."

if exist ".venv\Scripts\activate.bat" (
  call ".venv\Scripts\activate.bat"
)

taskkill /F /IM "BIMobile API Manager.exe" >nul 2>&1
taskkill /F /IM "BIMobile API Manager" >nul 2>&1

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

python -m PyInstaller ^
  --clean ^
  --onefile ^
  --windowed ^
  --name "BIMobile API Manager" ^
  --add-data "data;data" ^
  --add-data "app;app" ^
  launcher\desktop_launcher.py

if not exist release mkdir release
if not exist release\data mkdir release\data
if not exist release\logs mkdir release\logs

copy /y "dist\BIMobile API Manager.exe" "release\BIMobile API Manager.exe"
copy /y "data\bases_config.json" "release\data\bases_config.json"
copy /y "data\permissions_config.json" "release\data\permissions_config.json"

if not exist "release\README_INSTALACAO.txt" (
  > "release\README_INSTALACAO.txt" (
    echo BIMobile API Manager
    echo.
    echo 1. Execute BIMobile API Manager.exe.
    echo 2. Cadastre ou selecione uma base Firebird.
    echo 3. A API inicia automaticamente ao abrir o gerenciador.
    echo 4. O gerenciador cria e atualiza os arquivos em .\data.
  )
)

echo Build concluido em release\BIMobile API Manager.exe
endlocal
