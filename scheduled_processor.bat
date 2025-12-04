@echo off
setlocal enabledelayedexpansion

echo ========================================
echo NZ Property Analyser - Scheduled Run
echo ========================================
echo.

REM Set paths
set "SCRIPT_DIR=%~dp0"
set "INPUT_FOLDER=%SCRIPT_DIR%input"
set "OUTPUT_FOLDER=%SCRIPT_DIR%output"
set "TEMP_EMAIL_SCRIPT=%TEMP%\send_email_%RANDOM%.ps1"

REM Try to find Python
set PYTHON_PATH=
if exist "C:\Users\OEM\AppData\Local\Python\pythoncore-3.14-64\python.exe" (
    set PYTHON_PATH=C:\Users\OEM\AppData\Local\Python\pythoncore-3.14-64\python.exe
) else if exist "%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe" (
    set PYTHON_PATH=%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe
) else (
    where python >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        set PYTHON_PATH=python
    ) else (
        where py >nul 2>&1
        if !ERRORLEVEL! EQU 0 (
            set PYTHON_PATH=py
        ) else (
            echo ERROR: Python not found!
            exit /b 1
        )
    )
)

echo Using Python: %PYTHON_PATH%
echo.

REM Check if input folder exists
if not exist "%INPUT_FOLDER%" (
    echo ERROR: Input folder not found: %INPUT_FOLDER%
    exit /b 1
)

REM Get list of Excel files in input folder
set "FILE_COUNT=0"
set "FILES_PROCESSED="

echo Scanning input folder for Excel files...
for %%F in ("%INPUT_FOLDER%\*.xlsx") do (
    set /a FILE_COUNT+=1
    set "CURRENT_FILE=%%~nxF"
    echo Found: !CURRENT_FILE!
    set "FILES_PROCESSED=!FILES_PROCESSED!!CURRENT_FILE! "
)

if %FILE_COUNT% EQU 0 (
    echo No Excel files found in input folder.
    echo Exiting...
    exit /b 0
)

echo.
echo Found %FILE_COUNT% file(s) to process
echo.

REM Create a list of existing output files before processing
set "EXISTING_FILES=%TEMP%\existing_outputs_%RANDOM%.txt"
dir /b "%OUTPUT_FOLDER%\*.xlsx" > "%EXISTING_FILES%" 2>nul

REM Process each file in both modes
for %%F in ("%INPUT_FOLDER%\*.xlsx") do (
    set "CURRENT_FILE=%%~nxF"
    echo ========================================
    echo Processing: !CURRENT_FILE!
    echo ========================================
    echo.
    
    REM Run flip mode
    echo Running FLIP mode...
    "%PYTHON_PATH%" "%SCRIPT_DIR%main.py" "%%F" --mode flip --background
    if !ERRORLEVEL! NEQ 0 (
        echo WARNING: Flip mode failed for !CURRENT_FILE!
    )
    echo.
    
    REM Run rental mode
    echo Running RENTAL mode...
    "%PYTHON_PATH%" "%SCRIPT_DIR%main.py" "%%F" --mode rental --background
    if !ERRORLEVEL! NEQ 0 (
        echo WARNING: Rental mode failed for !CURRENT_FILE!
    )
    echo.
)

echo.
echo ========================================
echo Processing Complete
echo ========================================
echo.

REM Collect output files created during this run
echo Collecting output files...
set "OUTPUT_FILES="
set "OUTPUT_COUNT=0"
set "NEW_FILES_LIST=%TEMP%\new_outputs_%RANDOM%.txt"

REM Compare current output files with existing ones to find new files
for %%F in ("%OUTPUT_FOLDER%\*.xlsx") do (
    set "FILE_NAME=%%~nxF"
    findstr /C:"!FILE_NAME!" "%EXISTING_FILES%" >nul 2>&1
    if !ERRORLEVEL! NEQ 0 (
        REM This is a new file created during this run
        echo %%~F >> "%NEW_FILES_LIST%"
        set /a OUTPUT_COUNT+=1
        echo   - %%~nxF
    )
)

REM Clean up temp file
del "%EXISTING_FILES%" >nul 2>&1

REM If no new files found, attach all recent files (fallback)
if %OUTPUT_COUNT% EQU 0 (
    echo No new output files detected. Attaching all files in output folder...
    for %%F in ("%OUTPUT_FOLDER%\*.xlsx") do (
        echo %%~F >> "%NEW_FILES_LIST%"
        set /a OUTPUT_COUNT+=1
        echo   - %%~nxF
    )
)

echo Found %OUTPUT_COUNT% output file(s)
echo.

REM Create PowerShell script to send email via Outlook COM
echo Creating email script...

REM Build list of processed files for email body
set "PROCESSED_LIST="
for %%F in ("%INPUT_FOLDER%\*.xlsx") do (
    set "PROCESSED_LIST=!PROCESSED_LIST!  - %%~nxF`n"
)

REM Create PowerShell script
(
echo $ErrorActionPreference = "Stop"
echo try {
echo     $outlook = New-Object -ComObject Outlook.Application
echo     $mail = $outlook.CreateItem(0^)
echo     $mail.To = "abbey.roy@gmail.com"
echo     $mail.Subject = "NZ Property Analyser - Scheduled Run Results"
echo     $body = "Scheduled property analysis run completed.`n`n"
echo     $body += "Files processed: %FILE_COUNT%`n"
echo     $body += "Output files generated: %OUTPUT_COUNT%`n`n"
echo     $body += "Input files processed:`n%PROCESSED_LIST%`n"
echo     $mail.Body = $body
echo     
) > "%TEMP_EMAIL_SCRIPT%"

REM Add attachments for each new output file
if %OUTPUT_COUNT% GTR 0 (
    if exist "%NEW_FILES_LIST%" (
        for /f "usebackq delims=" %%F in ("%NEW_FILES_LIST%") do (
            echo     $mail.Attachments.Add("%%~F"^) >> "%TEMP_EMAIL_SCRIPT%"
        )
    ) else (
        REM Fallback: attach all files if list file doesn't exist
        for %%F in ("%OUTPUT_FOLDER%\*.xlsx") do (
            echo     $mail.Attachments.Add("%%~F"^) >> "%TEMP_EMAIL_SCRIPT%"
        )
    )
) else (
    echo     $mail.Body += "`n`nWARNING: No output files were generated." >> "%TEMP_EMAIL_SCRIPT%"
)

REM Clean up new files list
if exist "%NEW_FILES_LIST%" del "%NEW_FILES_LIST%" >nul 2>&1

REM Complete the PowerShell script
(
echo     
echo     $mail.Send^(^)
echo     Write-Host "Email sent successfully"
echo } catch {
echo     Write-Host "Error sending email: $_"
echo     exit 1
echo }
) >> "%TEMP_EMAIL_SCRIPT%"

REM Execute PowerShell script to send email
echo Sending email via Outlook...
powershell.exe -ExecutionPolicy Bypass -File "%TEMP_EMAIL_SCRIPT%"
set "EMAIL_ERROR=!ERRORLEVEL!"

REM Clean up temp script
del "%TEMP_EMAIL_SCRIPT%" >nul 2>&1

if !EMAIL_ERROR! EQU 0 (
    echo Email sent successfully!
) else (
    echo WARNING: Failed to send email. Results are available in: %OUTPUT_FOLDER%
)

echo.
echo ========================================
echo Scheduled Run Complete
echo ========================================
echo Output files location: %OUTPUT_FOLDER%
echo.

endlocal

