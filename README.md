# NZ Property Analyser

A Python application for analyzing New Zealand property investments in flip and rental modes.

## Features

- **Flip Calculator**: Calculate ROI, Cash on Cash ROI, and identify good deals
- **Rental Calculator**: Calculate Gross/Net Yield and identify successful rental properties
- **Duplicate Detection**: Automatically removes duplicate properties by URL
- **Stress Keyword Detection**: Identifies properties with sale stress indicators
- **Excel Output**: Generates detailed Excel reports with highlighting
- **Comprehensive Logging**: All calculations logged per file

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

1. **Clone or download this repository**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Project Structure

```
NZ Property Analyser/
├── input/              # Place your Excel input files here
├── output/             # Generated analysis files appear here
├── logs/               # Log files for each processing run
├── main.py             # Main entry point
├── config.py           # Configuration constants
├── requirements.txt    # Python dependencies
└── [other modules]     # Core processing modules
```

## Quick Start

### 1. Prepare Your Data

Place your Excel file(s) in the `input` folder. The file should contain columns like:
- `Property URL`
- `Listing Date`
- `Property Title`
- `Property Address`
- `Display Price`
- `Estimated Market Price`
- `Nearby Properties`
- `District`
- `Description`

### 2. Run the Program

#### Foreground Mode (Interactive)
```bash
python main.py input/your_file.xlsx --mode flip
```
- Will prompt you for an email address
- Shows all output on screen

#### Background Mode (Automated)
```bash
python main.py input/your_file.xlsx --mode flip --background
```
- Uses default email: abbey.roy@gmail.com
- Suitable for scheduled/automated runs

### 3. View Results

- **Excel Output**: Check the `output` folder for the generated analysis file
- **Logs**: Check the `logs` folder for detailed processing logs

## Command Line Options

```bash
python main.py [FILES] [OPTIONS]

Positional Arguments:
  files                 One or more Excel files (can use just filename if in input folder)

Options:
  --mode {flip,rental}  Calculation mode (default: flip)
  --background          Run in background mode (uses default email)
  --output OUTPUT       Custom output file path (optional)
```

## Examples

### Example 1: Analyze a single file in flip mode
```bash
python main.py residential_sale.xlsx --mode flip
```

### Example 2: Analyze multiple files in rental mode
```bash
python main.py file1.xlsx file2.xlsx --mode rental --background
```

### Example 3: Specify custom output file
```bash
python main.py residential_sale.xlsx --mode flip --output my_results.xlsx
```

### Example 4: Process file from input folder (recommended)
```bash
# Place file in input/ folder first, then:
python main.py residential_sale.xlsx --mode flip --background
```

## Calculation Modes

### Flip Mode
Calculates:
- Potential Purchase Price
- Potential Sale Price (from nearby properties)
- Renovation Budget (15% of purchase price)
- Holding Costs (2.5% of purchase price)
- Disposal Costs (3% of sale price)
- Contingency (1.5% of renovation budget)
- Profit
- ROI %
- Cash on Cash ROI %

**Good Deal Criteria**: ROI > 20% OR Cash on Cash ROI > 20%

### Rental Mode
Calculates:
- Weekly Rent (from rental data by district)
- Annual Rent
- Gross Yield
- Net Yield
- Net Income/Loss

**Success Criteria**: Net Yield > 4% AND Net Annual Income > -$5,000

## Output Files

The program generates Excel files with multiple sheets:

1. **Summary**: All properties with calculated values
2. **Good Deals**: Properties meeting success criteria (highlighted in green)
3. **Stress Sales**: Properties with stress keywords (highlighted in yellow)
4. **Metadata**: Processing information and configuration

## Logging

- Log files are created in the `logs` folder
- Each run creates a timestamped log file named after the input file
- Format: `{input_filename}_{timestamp}.log`
- Example: `residential_sale_20251203_130115.log`

## Troubleshooting

### Common Issues

1. **File not found**
   - Ensure your Excel file is in the `input` folder
   - Or provide the full path to the file

2. **Missing dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Column errors**
   - Ensure your Excel file has the required columns
   - Check column names match exactly (case-sensitive)

4. **No results found**
   - Check the log file for detailed error messages
   - Verify your data has valid price information

## Configuration

Edit `config.py` to customize:
- Default email address
- Stress keywords
- Calculation percentages
- Thresholds for good deals/success criteria

## Support

For issues or questions, check the log files in the `logs` folder for detailed error messages.

