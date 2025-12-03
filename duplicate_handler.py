"""
Duplicate detection and removal for property listings
"""
import pandas as pd
from logger import setup_logger

logger = setup_logger(__name__)


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove duplicate properties based on Property URL.
    For duplicates, keeps the entry with the latest Listing Date.
    
    Args:
        df: DataFrame with Property URL and Listing Date columns
        
    Returns:
        DataFrame with duplicates removed
    """
    if 'Property URL' not in df.columns:
        logger.warning("'Property URL' column not found, cannot remove duplicates")
        return df
    
    if 'Listing Date' not in df.columns:
        logger.warning("'Listing Date' column not found, cannot remove duplicates")
        return df
    
    initial_count = len(df)
    
    # Convert Listing Date to datetime if it's not already
    if df['Listing Date'].dtype == 'object':
        df['Listing Date'] = pd.to_datetime(df['Listing Date'], errors='coerce')
    
    # Sort by Listing Date descending (latest first)
    df_sorted = df.sort_values('Listing Date', ascending=False, na_position='last')
    
    # Keep first occurrence of each Property URL (which will be the latest date)
    df_unique = df_sorted.drop_duplicates(subset=['Property URL'], keep='first')
    
    # Reset index
    df_unique = df_unique.reset_index(drop=True)
    
    duplicates_removed = initial_count - len(df_unique)
    
    if duplicates_removed > 0:
        logger.info(f"Removed {duplicates_removed} duplicate entries. Kept {len(df_unique)} unique properties.")
    else:
        logger.info(f"No duplicates found. {len(df_unique)} properties processed.")
    
    return df_unique

