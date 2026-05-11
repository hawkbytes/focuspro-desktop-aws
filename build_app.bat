@echo off
echo ====================================
echo Building DDS Focus Pro Application
echo ====================================
echo.

cd /d "%~dp0"

echo Activating virtual environment...
call ..\..venv\Scripts\activate.bat

echo.
echo Starting PyInstaller build...
echo This may take several minutes...
echo.

pyinstaller connector.spec --noconfirm --clean

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ====================================
    echo BUILD SUCCESSFUL!
    echo ====================================
    echo.
    echo Executable created at: dist\connector.exe
    echo.
) else (
    echo.
    echo ====================================
    echo BUILD FAILED!
    echo ====================================
    echo Please check the error messages above.
    echo.
)

pause
