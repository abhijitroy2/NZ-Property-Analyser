@echo off
echo NZ Property Analyser - Rental Mode
echo.

REM Try to find Python
set PYTHON_PATH=
if exist "C:\Users\OEM\AppData\Local\Python\pythoncore-3.14-64\python.exe" (
    set PYTHON_PATH=C:\Users\OEM\AppData\Local\Python\pythoncore-3.14-64\python.exe
) else if exist "%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe" (
    set PYTHON_PATH=%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe
) else (
    REM Try common Python locations
    where python >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set PYTHON_PATH=python
    ) else (
        where py >nul 2>&1
        if %ERRORLEVEL% EQU 0 (
            set PYTHON_PATH=py
        ) else (
            echo ERROR: Python not found!
            echo Please install Python or add it to your PATH
            pause
            exit /b 1
        )
    )
)

echo Using Python: %PYTHON_PATH%
echo Processing residential_sale.xlsx...
echo.

"%PYTHON_PATH%" main.py residential_sale.xlsx --mode rental --background

echo.
echo Done! Check the output folder for results.
pause

