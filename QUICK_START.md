# Quick Start Guide - NZ Property Analyser

## Step-by-Step Instructions

### Step 1: Verify Python Installation

Open PowerShell or Command Prompt and check if Python is installed:

```powershell
python --version
```

If Python is not found, try:
```powershell
py --version
```

Or check the full path (we've been using):
```
C:\Users\OEM\AppData\Local\Python\pythoncore-3.14-64\python.exe
```

### Step 2: Install Dependencies

Navigate to the project folder:
```powershell
cd "C:\Users\OEM\NZ Property Analyser"
```

Install required packages:
```powershell
python -m pip install -r requirements.txt
```

Or if `python` doesn't work:
```powershell
py -m pip install -r requirements.txt
```

### Step 3: Prepare Your Input File

1. Place your Excel file in the `input` folder
2. Example: `input/residential_sale.xlsx`

### Step 4: Run the Program

#### Option A: Foreground Mode (Interactive)
```powershell
python main.py residential_sale.xlsx --mode flip
```

You'll be prompted to enter your email address.

#### Option B: Background Mode (Automated)
```powershell
python main.py residential_sale.xlsx --mode flip --background
```

Uses default email (abbey.roy@gmail.com) automatically.

#### Option C: Rental Mode
```powershell
python main.py residential_sale.xlsx --mode rental --background
```

### Step 5: Check Results

1. **Excel Output**: Look in `output/` folder
   - File name: `residential_sale_analysis_flip_YYYYMMDD_HHMMSS.xlsx`

2. **Logs**: Look in `logs/` folder
   - File name: `residential_sale_YYYYMMDD_HHMMSS.log`

## Common Commands Reference

```powershell
# Basic usage - flip mode
python main.py input/residential_sale.xlsx --mode flip

# Background mode (no email prompt)
python main.py input/residential_sale.xlsx --mode flip --background

# Rental mode
python main.py input/residential_sale.xlsx --mode rental --background

# Multiple files
python main.py input/file1.xlsx input/file2.xlsx --mode flip --background

# Custom output file
python main.py input/residential_sale.xlsx --mode flip --output my_results.xlsx --background
```

## Troubleshooting

### If `python` command doesn't work:

1. **Try `py` instead:**
   ```powershell
   py main.py residential_sale.xlsx --mode flip
   ```

2. **Use full path:**
   ```powershell
   C:\Users\OEM\AppData\Local\Python\pythoncore-3.14-64\python.exe main.py residential_sale.xlsx --mode flip
   ```

3. **Check Python installation:**
   - Open PowerShell
   - Run: `Get-Command python*`
   - Or: `where.exe python`

### If you get "Module not found" errors:

```powershell
python -m pip install pandas openpyxl python-dateutil
```

### If file not found:

- Make sure the file is in the `input` folder
- Or provide the full path: `python main.py "C:\full\path\to\file.xlsx" --mode flip`

## Example Workflow

1. **Open PowerShell** in the project directory
2. **Place file**: Copy `residential_sale.xlsx` to `input/` folder
3. **Run command**:
   ```powershell
   python main.py residential_sale.xlsx --mode flip --background
   ```
4. **Wait for completion** (usually 1-2 seconds for 100 properties)
5. **Check output**: Open `output/residential_sale_analysis_flip_*.xlsx`
6. **Review logs**: Check `logs/residential_sale_*.log` for details

## What You'll See

When running, you'll see output like:
```
2025-12-03 13:01:15 - INFO - Background mode: Using default email abbey.roy@gmail.com
2025-12-03 13:01:15 - INFO - Email address: abbey.roy@gmail.com
2025-12-03 13:01:15 - INFO - ============================================================
2025-12-03 13:01:15 - INFO - NZ Property Analyser - Starting Processing
2025-12-03 13:01:15 - INFO - ============================================================
2025-12-03 13:01:15 - INFO - Log file: residential_sale_20251203_130115.log
2025-12-03 13:01:15 - INFO - Starting property processing in flip mode
...
2025-12-03 13:01:18 - INFO - Processing completed successfully!
2025-12-03 13:01:18 - INFO - Total properties processed: 296
2025-12-03 13:01:18 - INFO - Good deals found: 79
2025-12-03 13:01:18 - INFO - Properties with stress keywords: 30
```

## Need Help?

- Check the `README.md` for detailed documentation
- Review log files in `logs/` folder for error details
- Verify your Excel file has all required columns

