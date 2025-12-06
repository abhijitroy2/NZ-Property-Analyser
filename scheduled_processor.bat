@echo off
setlocal enabledelayedexpansion

REM Set paths
set "SCRIPT_DIR=%~dp0"
set "INPUT_FOLDER=%SCRIPT_DIR%input"
set "OUTPUT_FOLDER=%SCRIPT_DIR%output"
set "EMAIL_LIST=%SCRIPT_DIR%email_list.txt"
set "TEMP_EMAIL_SCRIPT=%TEMP%\send_email_%RANDOM%.ps1"
set "LOGS_FOLDER=%SCRIPT_DIR%logs"

REM Create logs folder if it doesn't exist
if not exist "%LOGS_FOLDER%" mkdir "%LOGS_FOLDER%"

REM Generate log filename with timestamp
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set "DATETIME=%%I"
set "DATETIME=%DATETIME:~0,14%"
set "LOG_FILE=%LOGS_FOLDER%\scheduled_processor_%DATETIME%.log"

REM Initialize log file
(
echo ========================================
echo NZ Property Analyser - Scheduled Run
echo Started: %DATE% %TIME%
echo Log file: %LOG_FILE%
echo ========================================
echo.
) > "%LOG_FILE%"

REM Redirect all output to log file
REM All echo statements and command output will be logged
call :main >> "%LOG_FILE%" 2>&1
exit /b %ERRORLEVEL%

:main
REM Main script execution starts here
echo [%TIME%] Starting scheduled processor execution...
echo.

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

REM Ensure output folder exists
if not exist "%OUTPUT_FOLDER%" (
    echo Creating output folder: %OUTPUT_FOLDER%
    mkdir "%OUTPUT_FOLDER%"
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
echo Creating snapshot of existing output files...
if exist "%OUTPUT_FOLDER%\*.xlsx" (
    dir /b "%OUTPUT_FOLDER%\*.xlsx" > "%EXISTING_FILES%" 2>nul
) else (
    REM Create empty file if no existing files
    echo. > "%EXISTING_FILES%"
)
echo Existing output files before processing:
type "%EXISTING_FILES%" 2>nul || echo   (none)
echo.

REM Process each file in both modes
set "PROCESSED_INPUT_FILES="
for %%F in ("%INPUT_FOLDER%\*.xlsx") do (
    set "CURRENT_FILE=%%~nxF"
    set "PROCESSED_INPUT_FILES=!PROCESSED_INPUT_FILES!!CURRENT_FILE! "
    echo ========================================
    echo Processing: !CURRENT_FILE!
    echo ========================================
    echo.
    
    REM Run flip mode
    echo Running FLIP mode for !CURRENT_FILE!...
    "%PYTHON_PATH%" "%SCRIPT_DIR%main.py" "%%F" --mode flip --background
    if !ERRORLEVEL! NEQ 0 (
        echo ERROR: Flip mode failed for !CURRENT_FILE! (Exit code: !ERRORLEVEL!^)
    ) else (
        echo Flip mode completed successfully for !CURRENT_FILE!
    )
    echo.
    
    REM Run rental mode
    echo Running RENTAL mode for !CURRENT_FILE!...
    "%PYTHON_PATH%" "%SCRIPT_DIR%main.py" "%%F" --mode rental --background
    if !ERRORLEVEL! NEQ 0 (
        echo ERROR: Rental mode failed for !CURRENT_FILE! (Exit code: !ERRORLEVEL!^)
    ) else (
        echo Rental mode completed successfully for !CURRENT_FILE!
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
echo Comparing output files...
if exist "%OUTPUT_FOLDER%\*.xlsx" (
    for %%F in ("%OUTPUT_FOLDER%\*.xlsx") do (
        set "FILE_NAME=%%~nxF"
        findstr /C:"!FILE_NAME!" "%EXISTING_FILES%" >nul 2>&1
        if !ERRORLEVEL! NEQ 0 (
            REM This is a new file created during this run
            echo %%~F >> "%NEW_FILES_LIST%"
            set /a OUTPUT_COUNT+=1
            echo   NEW: %%~nxF
        ) else (
            echo   EXISTING: %%~nxF
        )
    )
) else (
    echo   No output files found in output folder
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

REM Check if email list file exists
if not exist "%EMAIL_LIST%" (
    echo ERROR: Email list file not found: %EMAIL_LIST%
    echo Please create email_list.txt with one email address per line.
    exit /b 1
)

REM Read email addresses from email_list.txt
echo Reading email addresses from email_list.txt...
set "EMAIL_RECIPIENTS="
set "EMAIL_COUNT=0"
for /f "usebackq eol=# tokens=* delims=" %%E in ("%EMAIL_LIST%") do (
    set "EMAIL_LINE=%%E"
    REM Skip empty lines
    if defined EMAIL_LINE (
        REM Remove leading whitespace only (tokens=* does this)
        for /f "tokens=*" %%L in ("!EMAIL_LINE!") do set "EMAIL_LINE=%%L"
        REM Remove trailing whitespace by checking if still defined
        if defined EMAIL_LINE (
            REM Check if it's a valid email (contains @)
            echo !EMAIL_LINE! | findstr "@" >nul 2>&1
            if !ERRORLEVEL! EQU 0 (
                if defined EMAIL_RECIPIENTS (
                    set "EMAIL_RECIPIENTS=!EMAIL_RECIPIENTS!;!EMAIL_LINE!"
                ) else (
                    set "EMAIL_RECIPIENTS=!EMAIL_LINE!"
                )
                set /a EMAIL_COUNT+=1
                echo   - !EMAIL_LINE!
            ) else (
                echo   Skipping invalid email: !EMAIL_LINE!
            )
        )
    )
)

if %EMAIL_COUNT% EQU 0 (
    echo ERROR: No valid email addresses found in email_list.txt
    exit /b 1
)

echo Found %EMAIL_COUNT% email address(es)
echo.

REM Create PowerShell script to send email via Outlook COM
echo Creating email script...

REM Build list of processed files for email body
set "PROCESSED_LIST="
for %%F in ("%INPUT_FOLDER%\*.xlsx") do (
    set "PROCESSED_LIST=!PROCESSED_LIST!  - %%~nxF`n"
)

REM Build list of output files for email body
set "OUTPUT_LIST="
if exist "%NEW_FILES_LIST%" (
    for /f "usebackq delims=" %%F in ("%NEW_FILES_LIST%") do (
        set "OUTPUT_LIST=!OUTPUT_LIST!  - %%~nxF`n"
    )
)

REM Create PowerShell script
(
echo $ErrorActionPreference = "Continue"
echo try {
echo     Write-Host "Connecting to Outlook..."
echo     $outlook = New-Object -ComObject Outlook.Application
echo     $mail = $outlook.CreateItem(0^)
echo     
echo     REM Set recipients - split by semicolon and add each one
echo     $recipients = "%EMAIL_RECIPIENTS%"
echo     $recipientArray = $recipients -split ";"
echo     foreach ($recipient in $recipientArray^) {
echo         $recipient = $recipient.Trim^(^)
echo         if ($recipient -ne ""^) {
echo             $mail.Recipients.Add($recipient^)
echo             Write-Host "Added recipient: $recipient"
echo         }
echo     }
echo     
echo     $mail.Subject = "NZ Property Analyser - Scheduled Run Results"
echo     $body = "Scheduled property analysis run completed.`n`n"
echo     $body += "Input files processed: %FILE_COUNT%`n"
echo     $body += "Output files generated: %OUTPUT_COUNT%`n`n"
echo     $body += "Input files:`n%PROCESSED_LIST%`n"
echo     if (%OUTPUT_COUNT% -gt 0^) {
echo         $body += "Output files:`n%OUTPUT_LIST%`n"
echo     } else {
echo         $body += "WARNING: No output files were generated.`n"
echo     }
echo     $mail.Body = $body
echo     
echo     REM Set sender display name to "Property Analyser"
echo     try {
echo         $namespace = $outlook.GetNamespace("MAPI"^)
echo         $accounts = $namespace.Accounts
echo         if ($accounts.Count -gt 0^) {
echo             $account = $accounts[0]
echo             REM Try to set sender display name using PropertyAccessor
echo             try {
echo                 $pa = $mail.PropertyAccessor
echo                 REM Set the sender name property (PR_SENDER_NAME)
echo                 $senderNameProp = "http://schemas.microsoft.com/mapi/proptag/0x0C1A001E"
echo                 $pa.SetProperty($senderNameProp, "Property Analyser"^)
echo                 Write-Host "Set sender display name to 'Property Analyser'"
echo             } catch {
echo                 Write-Host "Warning: Could not set sender display name: $_"
echo             }
echo         }
echo     } catch {
echo         Write-Host "Warning: Could not access Outlook accounts: $_"
echo     }
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
echo     Write-Host "Sending email..."
echo     $mail.Send^(^)
echo     Write-Host "Email sent successfully to all recipients"
echo } catch {
echo     Write-Host "ERROR sending email: $_"
echo     Write-Host "Error details: $($_.Exception.Message^)"
echo     if ($_.Exception.InnerException^) {
echo         Write-Host "Inner exception: $($_.Exception.InnerException.Message^)"
echo     }
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
echo Completed: %DATE% %TIME%
echo Output files location: %OUTPUT_FOLDER%
echo Log file: %LOG_FILE%
echo ========================================
echo.

exit /b 0
