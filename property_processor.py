"""
Main property processing pipeline
"""
import pandas as pd
import os
from pathlib import Path
from typing import List, Optional
from data_loader import load_excel_file, prepare_property_data
from duplicate_handler import remove_duplicates
from flip_calculator import calculate_flip_metrics
from rental_calculator import calculate_rental_metrics
from output_generator import create_excel_output
from config import STRESS_KEYWORDS
from logger import setup_logger

logger = setup_logger(__name__)

# Output folder path
OUTPUT_FOLDER = "output"


def detect_stress_keywords(row: pd.Series) -> bool:
    """
    Detect if property has stress keywords in Title or Description.
    
    Args:
        row: Property row from DataFrame
        
    Returns:
        True if stress keywords found, False otherwise
    """
    text_to_check = []
    
    # Check Property Title
    if 'Property Title' in row and pd.notna(row.get('Property Title')):
        text_to_check.append(str(row['Property Title']).lower())
    
    # Check Description
    if 'Description' in row and pd.notna(row.get('Description')):
        text_to_check.append(str(row['Description']).lower())
    
    # Combine all text
    combined_text = ' '.join(text_to_check)
    
    # Check for stress keywords (case-insensitive)
    for keyword in STRESS_KEYWORDS:
        if keyword.lower() in combined_text:
            logger.debug(f"Found stress keyword '{keyword}' in property")
            return True
    
    return False


def process_properties(file_paths: List[str], mode: str = "flip", output_file: Optional[str] = None) -> pd.DataFrame:
    """
    Process property files through the complete pipeline.
    
    Args:
        file_paths: List of input file paths
        mode: Calculation mode ("flip" or "rental")
        output_file: Optional output file path. If None, generates based on input file.
        
    Returns:
        DataFrame with all calculated metrics
    """
    logger.info(f"Starting property processing in {mode} mode")
    logger.info(f"Processing {len(file_paths)} file(s)")
    
    # Step 1: Load all files and combine
    all_dataframes = []
    for file_path in file_paths:
        logger.info(f"Loading file: {file_path}")
        df = load_excel_file(file_path)
        all_dataframes.append(df)
    
    # Combine all DataFrames
    if len(all_dataframes) > 1:
        combined_df = pd.concat(all_dataframes, ignore_index=True)
        logger.info(f"Combined {len(all_dataframes)} files into {len(combined_df)} total rows")
    else:
        combined_df = all_dataframes[0]
    
    # Step 2: Prepare data (parse prices, etc.)
    logger.info("Preparing property data...")
    combined_df = prepare_property_data(combined_df)
    
    # Step 3: Remove duplicates
    logger.info("Removing duplicates...")
    combined_df = remove_duplicates(combined_df)
    
    # Step 4: Process each property
    logger.info(f"Processing {len(combined_df)} properties...")
    
    # Initialize result columns
    combined_df['Has_Stress_Keywords'] = False
    
    # Process each row
    for idx, row in combined_df.iterrows():
        logger.info(f"Processing property {idx + 1}/{len(combined_df)}: {row.get('Property Address', 'Unknown')}")
        
        # Detect stress keywords
        has_stress = detect_stress_keywords(row)
        combined_df.at[idx, 'Has_Stress_Keywords'] = has_stress
        
        # Calculate metrics based on mode
        if mode == "flip":
            flip_metrics = calculate_flip_metrics(row)
            
            # Add flip metrics to DataFrame
            for key, value in flip_metrics.items():
                # Convert lists to strings for DataFrame storage
                if isinstance(value, list):
                    combined_df.at[idx, key] = ', '.join(str(v) for v in value) if value else ''
                else:
                    combined_df.at[idx, key] = value
            
            # Log calculations
            logger.debug(f"Property {idx + 1} - Flip Metrics:")
            logger.debug(f"  Potential Purchase Price: ${flip_metrics.get('Potential_Purchase_Price', 'N/A')}")
            logger.debug(f"  Potential Sale Price: ${flip_metrics.get('Potential_Sale_Price', 'N/A')}")
            logger.debug(f"  Profit: ${flip_metrics.get('Profit', 'N/A')}")
            logger.debug(f"  ROI: {flip_metrics.get('ROI_Percent', 'N/A')}%")
            logger.debug(f"  Cash on Cash ROI: {flip_metrics.get('Cash_on_Cash_ROI_Percent', 'N/A')}%")
            
            if flip_metrics.get('Calculation_Errors'):
                logger.warning(f"Property {idx + 1} calculation errors: {flip_metrics['Calculation_Errors']}")
        
        elif mode == "rental":
            rental_metrics = calculate_rental_metrics(row)
            
            # Add rental metrics to DataFrame
            for key, value in rental_metrics.items():
                # Convert lists to strings for DataFrame storage
                if isinstance(value, list):
                    combined_df.at[idx, key] = ', '.join(str(v) for v in value) if value else ''
                else:
                    combined_df.at[idx, key] = value
            
            # Log calculations
            logger.debug(f"Property {idx + 1} - Rental Metrics:")
            logger.debug(f"  Potential Purchase Price: ${rental_metrics.get('Potential_Purchase_Price', 'N/A')}")
            logger.debug(f"  Weekly Rent: ${rental_metrics.get('Weekly_Rent', 'N/A')}")
            logger.debug(f"  Annual Rent: ${rental_metrics.get('Annual_Rent', 'N/A')}")
            logger.debug(f"  Gross Yield: {rental_metrics.get('Gross_Yield_Percent', 'N/A')}%")
            
            if rental_metrics.get('Gross_Yield_Below_Threshold'):
                logger.info(f"Property {idx + 1} - Gross Yield below 5%, stopping calculation")
            else:
                logger.debug(f"  Net Yield: {rental_metrics.get('Net_Yield_Percent', 'N/A')}%")
                logger.debug(f"  Net Income: ${rental_metrics.get('Net_Income_Loss', 'N/A')}")
            
            if rental_metrics.get('Calculation_Errors'):
                logger.warning(f"Property {idx + 1} calculation errors: {rental_metrics['Calculation_Errors']}")
        
        else:
            logger.error(f"Unknown mode: {mode}")
            return combined_df
    
    # Step 5: Generate output Excel file
    # Ensure output folder exists
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    
    if output_file is None:
        # Generate output filename based on first input file
        # Extract just the filename without path
        first_file = file_paths[0]
        base_name = os.path.basename(first_file).replace('.xlsx', '').replace('.xls', '')
        output_file = f"{base_name}_analysis_{mode}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    # If output_file is not absolute, save to output folder
    if not os.path.isabs(output_file):
        output_file = os.path.join(OUTPUT_FOLDER, output_file)
    
    logger.info(f"Generating output Excel file: {output_file}")
    create_excel_output(combined_df, output_file, mode)
    
    # Step 6: Filter successful results
    if mode == "flip":
        successful_df = combined_df[combined_df.get('Is_Good_Deal', False) == True]
        logger.info(f"Found {len(successful_df)} successful flip properties (good deals)")
    else:  # rental
        successful_df = combined_df[combined_df.get('Is_Successful', False) == True]
        logger.info(f"Found {len(successful_df)} successful rental properties")
    
    logger.info("Property processing completed")
    
    return combined_df


def get_successful_properties(df: pd.DataFrame, mode: str) -> pd.DataFrame:
    """
    Get successful properties based on mode.
    
    Args:
        df: DataFrame with calculated metrics
        mode: Calculation mode ("flip" or "rental")
        
    Returns:
        DataFrame with only successful properties
    """
    if mode == "flip":
        if 'Is_Good_Deal' in df.columns:
            return df[df['Is_Good_Deal'] == True]
        else:
            return pd.DataFrame()
    else:  # rental
        if 'Is_Successful' in df.columns:
            return df[df['Is_Successful'] == True]
        else:
            return pd.DataFrame()

