# NZ Property Analyser - Flip Mode (PowerShell Script)

Write-Host "NZ Property Analyser - Flip Mode" -ForegroundColor Cyan
Write-Host ""

# Try to find Python
$pythonPath = $null

# Check known location first
$knownPath = "C:\Users\OEM\AppData\Local\Python\pythoncore-3.14-64\python.exe"
if (Test-Path $knownPath) {
    $pythonPath = $knownPath
    Write-Host "Found Python at: $pythonPath" -ForegroundColor Green
}
else {
    # Try to find Python in common locations
    $possiblePaths = @(
        "$env:LOCALAPPDATA\Python\pythoncore-3.14-64\python.exe",
        "$env:PROGRAMFILES\Python*\python.exe",
        "$env:PROGRAMFILES(X86)\Python*\python.exe"
    )
    
    foreach ($path in $possiblePaths) {
        $found = Get-Command $path -ErrorAction SilentlyContinue
        if ($found) {
            $pythonPath = $found.Source
            break
        }
    }
    
    # Try 'python' or 'py' commands
    if (-not $pythonPath) {
        $found = Get-Command python -ErrorAction SilentlyContinue
        if ($found) {
            $pythonPath = "python"
        }
        else {
            $found = Get-Command py -ErrorAction SilentlyContinue
            if ($found) {
                $pythonPath = "py"
            }
        }
    }
}

if (-not $pythonPath) {
    Write-Host "ERROR: Python not found!" -ForegroundColor Red
    Write-Host "Please install Python or add it to your PATH" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Processing residential_sale.xlsx..." -ForegroundColor Yellow
Write-Host ""

# Run the program
& $pythonPath main.py residential_sale.xlsx --mode flip --background

Write-Host ""
Write-Host "Done! Check the output folder for results." -ForegroundColor Green
Read-Host "Press Enter to exit"

