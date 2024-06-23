@echo off
setlocal

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed. Installing Python...
    REM Adjust the Python installer path and options as necessary
    REM For example, download and run the installer silently
    REM curl -o python-installer.exe https://www.python.org/ftp/python/3.x.x/python-3.x.x.exe
    REM start /wait python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
    echo Please install Python manually from https://www.python.org/downloads/ and rerun this script.
    exit /b 1
)

REM Create a virtual environment
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate the virtual environment
call venv\Scripts\activate

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install necessary packages
echo Installing necessary packages...
pip install pyqt5 pyinstaller plyer requests

REM Instructions to run the applications
echo.
echo Environment setup is complete.
echo.
echo To run the ClientBuilder, use:
echo python client_builder.py
echo.
echo To run the Server, use:
echo python server_gui.py
echo.

endlocal
pause
