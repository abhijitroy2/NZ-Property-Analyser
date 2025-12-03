# How to Run NZ Property Analyser - Visual Guide

## 🚀 Quick Start (3 Steps)

### Step 1: Open Terminal
- Press `Windows Key + R`
- Type `powershell` and press Enter
- Navigate to project folder:
  ```powershell
  cd "C:\Users\OEM\NZ Property Analyser"
  ```

### Step 2: Run the Program

**Easiest Way - Double-click batch file:**
- Double-click `run_flip.bat` for flip mode
- Double-click `run_rental.bat` for rental mode

**Or use command line:**

For **Flip Mode**:
```powershell
python main.py residential_sale.xlsx --mode flip --background
```

For **Rental Mode**:
```powershell
python main.py residential_sale.xlsx --mode rental --background
```

### Step 3: Check Results
- Open `output` folder
- Find the newest Excel file (sorted by date)
- Open it to see your analysis results

---

## 📋 Detailed Walkthrough

### Method 1: Using Batch Files (Easiest)

1. **Ensure your Excel file is in the `input` folder**
   - File: `input/residential_sale.xlsx`

2. **Double-click one of these files:**
   - `run_flip.bat` → Analyzes in flip mode
   - `run_rental.bat` → Analyzes in rental mode

3. **Wait for completion** (1-2 seconds)

4. **Results appear in `output` folder**

### Method 2: Using Command Line

1. **Open PowerShell:**
   - Press `Windows Key + X`
   - Select "Windows PowerShell" or "Terminal"

2. **Navigate to project:**
   ```powershell
   cd "C:\Users\OEM\NZ Property Analyser"
   ```

3. **Run command:**
   ```powershell
   python main.py residential_sale.xlsx --mode flip --background
   ```

4. **What you'll see:**
   ```
   2025-12-03 13:01:15 - INFO - Background mode: Using default email...
   2025-12-03 13:01:15 - INFO - Starting property processing in flip mode
   2025-12-03 13:01:15 - INFO - Loading file: input\residential_sale.xlsx
   2025-12-03 13:01:15 - INFO - Loaded 296 rows from input\residential_sale.xlsx
   ...
   2025-12-03 13:01:18 - INFO - Processing completed successfully!
   2025-12-03 13:01:18 - INFO - Total properties processed: 296
   2025-12-03 13:01:18 - INFO - Good deals found: 79
   ```

5. **Check results:**
   - Go to `output` folder
   - Open the Excel file (most recent one)

---

## 📁 File Locations

```
NZ Property Analyser/
│
├── input/                          ← Put your Excel files here
│   └── residential_sale.xlsx
│
├── output/                         ← Results appear here
│   └── residential_sale_analysis_flip_20251203_130117.xlsx
│
├── logs/                           ← Log files here
│   └── residential_sale_20251203_130115.log
│
├── run_flip.bat                    ← Double-click to run flip mode
├── run_rental.bat                  ← Double-click to run rental mode
└── main.py                         ← Main program file
```

---

## 🎯 Common Scenarios

### Scenario 1: Analyze a New File

1. Copy your Excel file to `input` folder
2. Rename it or remember the filename
3. Run:
   ```powershell
   python main.py input/your_new_file.xlsx --mode flip --background
   ```

### Scenario 2: Analyze Multiple Files

```powershell
python main.py input/file1.xlsx input/file2.xlsx --mode flip --background
```

### Scenario 3: Get Interactive Mode (with email prompt)

```powershell
python main.py residential_sale.xlsx --mode flip
# (Remove --background flag to get email prompt)
```

### Scenario 4: Custom Output Filename

```powershell
python main.py residential_sale.xlsx --mode flip --output my_custom_results.xlsx --background
```

---

## ⚙️ Command Options Explained

| Option | Description | Example |
|--------|-------------|---------|
| `--mode flip` | Calculate flip metrics (ROI, profit) | `--mode flip` |
| `--mode rental` | Calculate rental metrics (yield, income) | `--mode rental` |
| `--background` | Use default email, no prompts | `--background` |
| `--output FILE` | Custom output filename | `--output results.xlsx` |

---

## 🔍 Understanding the Output

### Excel File Contains 4 Sheets:

1. **Summary Sheet**
   - All properties with all calculated values
   - Green highlighting = Good deals
   - Yellow highlighting = Stress sales

2. **Good Deals Sheet**
   - Only properties meeting success criteria
   - All highlighted in green

3. **Stress Sales Sheet**
   - Properties with stress keywords
   - All highlighted in yellow

4. **Metadata Sheet**
   - Processing date, mode, configuration
   - Thresholds and settings used

### Log File Contains:
- Detailed calculation steps for each property
- Error messages if any
- Processing statistics
- Timestamp of each operation

---

## ❓ Troubleshooting

### Problem: "python is not recognized"

**Solution 1:** Try `py` instead:
```powershell
py main.py residential_sale.xlsx --mode flip --background
```

**Solution 2:** Use full path:
```powershell
C:\Users\OEM\AppData\Local\Python\pythoncore-3.14-64\python.exe main.py residential_sale.xlsx --mode flip --background
```

### Problem: "Module not found"

**Solution:** Install dependencies:
```powershell
python -m pip install -r requirements.txt
```

### Problem: "File not found"

**Solution:** 
- Check file is in `input` folder
- Or use full path: `python main.py "C:\full\path\to\file.xlsx" --mode flip`

### Problem: No results in output

**Solution:**
- Check log file in `logs` folder for errors
- Verify Excel file has required columns
- Check console output for error messages

---

## 📊 Performance

- **100 properties**: ~0.5-1 second
- **296 properties**: ~1-2 seconds
- **1000 properties**: ~3-5 seconds

The program processes properties sequentially and logs progress in real-time.

---

## 💡 Tips

1. **Use background mode** for automated runs (no email prompt)
2. **Check logs folder** if something goes wrong
3. **Keep input files organized** in the input folder
4. **Output files are timestamped** - old ones won't be overwritten
5. **Log files are named per input file** - easy to track

---

## 🎓 Next Steps

- Read `README.md` for detailed documentation
- Check `config.py` to customize thresholds
- Review log files to understand calculations
- Modify stress keywords in `config.py` if needed

