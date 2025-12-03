"""
Excel output generator with highlighting and multiple sheets
"""
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment
from openpyxl.utils.dataframe import dataframe_to_rows
from datetime import datetime
from typing import List, Optional
from logger import setup_logger

logger = setup_logger(__name__)

# Color definitions
GREEN_FILL = PatternFill(start_color="90EE90", end_color="90EE90", fill_type="solid")  # Light green
YELLOW_FILL = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")  # Yellow
HEADER_FILL = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")  # Blue
HEADER_FONT = Font(bold=True, color="FFFFFF")


def create_excel_output(df: pd.DataFrame, output_file: str, mode: str = "flip"):
    """
    Create Excel output file with multiple sheets and highlighting.
    
    Args:
        df: DataFrame with all property data and calculated metrics
        output_file: Path to output Excel file
        mode: Calculation mode ("flip" or "rental")
    """
    try:
        wb = Workbook()
        wb.remove(wb.active)  # Remove default sheet
        
        # Create Summary sheet with all properties
        summary_sheet = wb.create_sheet("Summary")
        write_dataframe_to_sheet(summary_sheet, df)
        apply_highlighting(summary_sheet, df, mode, highlight_all=True)
        
        # Create Good Deals sheet
        if mode == "flip":
            if 'Is_Good_Deal' in df.columns:
                good_deals_df = df[df['Is_Good_Deal'] == True]
            else:
                good_deals_df = pd.DataFrame()
        else:  # rental
            if 'Is_Successful' in df.columns:
                good_deals_df = df[df['Is_Successful'] == True]
            else:
                good_deals_df = pd.DataFrame()
        
        if not good_deals_df.empty:
            good_deals_sheet = wb.create_sheet("Good Deals")
            write_dataframe_to_sheet(good_deals_sheet, good_deals_df)
            apply_highlighting(good_deals_sheet, good_deals_df, mode, highlight_all=False)
            logger.info(f"Created Good Deals sheet with {len(good_deals_df)} properties")
        else:
            logger.info("No good deals found, skipping Good Deals sheet")
        
        # Create Stress Sales sheet
        if 'Has_Stress_Keywords' in df.columns:
            stress_sales_df = df[df['Has_Stress_Keywords'] == True]
        else:
            stress_sales_df = pd.DataFrame()
        if not stress_sales_df.empty:
            stress_sheet = wb.create_sheet("Stress Sales")
            write_dataframe_to_sheet(stress_sheet, stress_sales_df)
            apply_highlighting(stress_sheet, stress_sales_df, mode, highlight_all=False)
            logger.info(f"Created Stress Sales sheet with {len(stress_sales_df)} properties")
        else:
            logger.info("No stress sales found, skipping Stress Sales sheet")
        
        # Create Metadata sheet
        metadata_sheet = wb.create_sheet("Metadata")
        write_metadata(metadata_sheet, mode, len(df))
        
        # Save workbook
        wb.save(output_file)
        logger.info(f"Excel file saved: {output_file}")
        
    except Exception as e:
        logger.error(f"Error creating Excel output: {str(e)}")
        raise


def write_dataframe_to_sheet(ws, df: pd.DataFrame):
    """
    Write DataFrame to worksheet.
    
    Args:
        ws: Worksheet object
        df: DataFrame to write
    """
    # Convert lists and other non-serializable types to strings before writing
    df_clean = df.copy()
    for col in df_clean.columns:
        df_clean[col] = df_clean[col].apply(
            lambda x: ', '.join(str(v) for v in x) if isinstance(x, list) else x
        )
    
    # Convert DataFrame to rows
    for r_idx, row in enumerate(dataframe_to_rows(df_clean, index=False, header=True), 1):
        for c_idx, value in enumerate(row, 1):
            cell = ws.cell(row=r_idx, column=c_idx)
            # Handle any remaining non-serializable types
            if isinstance(value, (list, dict)):
                cell.value = str(value)
            else:
                cell.value = value
            
            # Format header row
            if r_idx == 1:
                cell.fill = HEADER_FILL
                cell.font = HEADER_FONT
                cell.alignment = Alignment(horizontal="center", vertical="center")
    
    # Auto-adjust column widths
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column_letter].width = adjusted_width


def apply_highlighting(ws, df: pd.DataFrame, mode: str, highlight_all: bool = True):
    """
    Apply highlighting to rows based on criteria.
    
    Args:
        ws: Worksheet object
        df: DataFrame with data
        mode: Calculation mode ("flip" or "rental")
        highlight_all: If True, highlight all rows. If False, only highlight specific rows.
    """
    if highlight_all:
        # Highlight good deals in green
        for row_idx, (idx, row) in enumerate(df.iterrows(), start=0):
            row_num = row_idx + 2  # +2 because row 1 is header, and DataFrame index starts at 0
            
            # Check if it's a good deal
            is_good_deal = False
            if mode == "flip":
                if 'Is_Good_Deal' in row.index:
                    is_good_deal = row['Is_Good_Deal'] == True
            else:  # rental
                if 'Is_Successful' in row.index:
                    is_good_deal = row['Is_Successful'] == True
            
            if is_good_deal:
                for col in range(1, len(df.columns) + 1):
                    ws.cell(row=row_num, column=col).fill = GREEN_FILL
            
            # Check if it has stress keywords
            has_stress = False
            if 'Has_Stress_Keywords' in row.index:
                has_stress = row['Has_Stress_Keywords'] == True
            if has_stress:
                for col in range(1, len(df.columns) + 1):
                    cell = ws.cell(row=row_num, column=col)
                    # If already green, don't override. Otherwise, make yellow.
                    current_fill = cell.fill
                    if current_fill is None or current_fill.start_color.rgb != GREEN_FILL.start_color.rgb:
                        cell.fill = YELLOW_FILL
    else:
        # For filtered sheets, all rows are already good deals or stress sales
        # So we just highlight them appropriately
        if ws.title == "Good Deals":
            for row_num in range(2, len(df) + 2):
                for col in range(1, len(df.columns) + 1):
                    ws.cell(row=row_num, column=col).fill = GREEN_FILL
        elif ws.title == "Stress Sales":
            for row_num in range(2, len(df) + 2):
                for col in range(1, len(df.columns) + 1):
                    ws.cell(row=row_num, column=col).fill = YELLOW_FILL


def write_metadata(ws, mode: str, num_properties: int):
    """
    Write metadata to worksheet.
    
    Args:
        ws: Worksheet object
        mode: Calculation mode
        num_properties: Number of properties processed
    """
    metadata = [
        ["NZ Property Analyser - Metadata"],
        [""],
        ["Processing Date", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        ["Calculation Mode", mode],
        ["Number of Properties Processed", num_properties],
        [""],
        ["Configuration"],
        ["Renovation Budget", "15% of Potential Purchase Price"],
        ["Holding Costs", "2.5% of Potential Purchase Price"],
        ["Disposal Costs", "3% of Potential Sale Price"],
        ["Contingency", "1.5% of Renovation Budget"],
        ["Cash on Cash Down Payment", "30% of Potential Purchase Price"],
        [""],
        ["Thresholds"],
        ["Flip ROI Threshold", "20%"],
        ["Rental Gross Yield Threshold", "5%"],
        ["Rental Net Yield Threshold", "4%"],
        ["Rental Net Income Threshold", "-$5,000"],
    ]
    
    for r_idx, row in enumerate(metadata, 1):
        for c_idx, value in enumerate(row, 1):
            cell = ws.cell(row=r_idx, column=c_idx)
            cell.value = value
            
            # Format header
            if r_idx == 1:
                cell.font = Font(bold=True, size=14)
            elif value in ["Configuration", "Thresholds"]:
                cell.font = Font(bold=True)
    
    # Auto-adjust column widths
    ws.column_dimensions['A'].width = 30
    ws.column_dimensions['B'].width = 40

