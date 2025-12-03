"""
Rental data loader for querying Detailed-Monthly-TLA-Tenancy-v2.csv
"""
import pandas as pd
from datetime import datetime
from typing import Optional
from config import RENTAL_DATA_FILE
from logger import setup_logger

logger = setup_logger(__name__)

# Cache for loaded rental data
_rental_data_cache = None
_latest_date_cache = None


def load_rental_data() -> pd.DataFrame:
    """
    Load the rental data CSV file.
    Uses caching to avoid reloading on multiple calls.
    
    Returns:
        DataFrame containing rental data
    """
    global _rental_data_cache
    
    if _rental_data_cache is not None:
        return _rental_data_cache
    
    try:
        df = pd.read_csv(RENTAL_DATA_FILE)
        logger.info(f"Loaded rental data from {RENTAL_DATA_FILE}: {len(df)} rows")
        
        # Parse Time Frame column to datetime
        df['Time Frame'] = pd.to_datetime(df['Time Frame'], format='%d/%m/%Y', errors='coerce')
        
        # Remove rows with invalid dates
        df = df[df['Time Frame'].notna()]
        
        _rental_data_cache = df
        return df
    except Exception as e:
        logger.error(f"Error loading rental data file {RENTAL_DATA_FILE}: {str(e)}")
        raise


def get_latest_date() -> Optional[datetime]:
    """
    Get the latest date in the rental data.
    
    Returns:
        Latest datetime, or None if no data
    """
    global _latest_date_cache
    
    if _latest_date_cache is not None:
        return _latest_date_cache
    
    df = load_rental_data()
    if df.empty:
        return None
    
    _latest_date_cache = df['Time Frame'].max()
    return _latest_date_cache


def normalize_district_name(district: str) -> str:
    """
    Normalize district name for matching (lowercase, strip whitespace).
    
    Args:
        district: District name from input file
        
    Returns:
        Normalized district name
    """
    if pd.isna(district) or not isinstance(district, str):
        return ""
    return district.strip().lower()


def get_upper_quartile_rent(district: str) -> Optional[float]:
    """
    Get Geometric Mean Rent for a given district.
    Matches district from input file to Location in rental data by latest date.
    
    Args:
        district: District name from property data
        
    Returns:
        Geometric Mean Rent value, or None if not found
    """
    if not district or pd.isna(district):
        return None
    
    try:
        df = load_rental_data()
        if df.empty:
            logger.warning("Rental data is empty")
            return None
        
        latest_date = get_latest_date()
        if latest_date is None:
            logger.warning("Could not determine latest date in rental data")
            return None
        
        # Filter by latest date
        latest_data = df[df['Time Frame'] == latest_date]
        
        if latest_data.empty:
            logger.warning(f"No data found for latest date {latest_date}")
            return None
        
        # Normalize district name for matching
        normalized_district = normalize_district_name(district)
        
        # Try exact match first
        match = latest_data[latest_data['Location'].str.lower().str.strip() == normalized_district]
        
        # If no exact match, try partial match (e.g., "Auckland" matches "Auckland")
        if match.empty:
            match = latest_data[
                latest_data['Location'].str.lower().str.strip().str.contains(
                    normalized_district, case=False, na=False, regex=False
                )
            ]
        
        # If still no match, try reverse (e.g., "Auckland" in "Auckland City")
        if match.empty:
            match = latest_data[
                latest_data['Location'].str.lower().str.strip().apply(
                    lambda x: normalized_district in x if isinstance(x, str) else False
                )
            ]
        
        if match.empty:
            logger.debug(f"No rental data found for district: {district}")
            return None
        
        # Get the first match (should be unique for a district)
        geometric_mean_rent = match.iloc[0]['Geometric Mean Rent']
        
        # Handle if it's a string with commas
        if isinstance(geometric_mean_rent, str):
            geometric_mean_rent = geometric_mean_rent.replace(',', '')
        
        try:
            return float(geometric_mean_rent)
        except (ValueError, TypeError):
            logger.warning(f"Could not convert Geometric Mean Rent to float: {geometric_mean_rent}")
            return None
        
    except Exception as e:
        logger.error(f"Error getting Geometric Mean Rent for district '{district}': {str(e)}")
        return None

