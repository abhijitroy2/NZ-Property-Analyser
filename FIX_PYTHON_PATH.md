# Fix Python Not Recognized Issue

## Problem
PowerShell says `python` or `py` commands are not recognized.

## Solution Options

### Option 1: Use the Updated Batch Files (Easiest)
The batch files (`run_flip.bat` and `run_rental.bat`) have been updated to automatically find Python. Just double-click them!

### Option 2: Use PowerShell Scripts
Double-click:
- `run_flip.ps1` (for flip mode)
- `run_rental.ps1` (for rental mode)

If you get an execution policy error, run this first in PowerShell:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Option 3: Use Full Path Directly

In PowerShell, use the full path to Python:

**Flip Mode:**
```powershell
C:\Users\OEM\AppData\Local\Python\pythoncore-3.14-64\python.exe main.py residential_sale.xlsx --mode flip --background
```

**Rental Mode:**
```powershell
C:\Users\OEM\AppData\Local\Python\pythoncore-3.14-64\python.exe main.py residential_sale.xlsx --mode rental --background
```

### Option 4: Add Python to PATH (Permanent Fix)

1. **Find Python location:**
   ```
   C:\Users\OEM\AppData\Local\Python\pythoncore-3.14-64\
   ```

2. **Add to PATH:**
   - Press `Windows Key + R`
   - Type `sysdm.cpl` and press Enter
   - Go to "Advanced" tab
   - Click "Environment Variables"
   - Under "User variables", find "Path" and click "Edit"
   - Click "New" and add: `C:\Users\OEM\AppData\Local\Python\pythoncore-3.14-64`
   - Click "OK" on all windows
   - Restart PowerShell

3. **Verify:**
   ```powershell
   python --version
   ```

### Option 5: Create an Alias (Quick Fix)

Add this to your PowerShell profile:

```powershell
# Open PowerShell profile
notepad $PROFILE

# Add this line:
Set-Alias python "C:\Users\OEM\AppData\Local\Python\pythoncore-3.14-64\python.exe"

# Save and restart PowerShell
```

## Recommended: Use the Batch Files

The easiest solution is to just use the updated batch files:
- `run_flip.bat` - Double-click to run flip mode
- `run_rental.bat` - Double-click to run rental mode

They will automatically find Python for you!

