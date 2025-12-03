"""
Data loading and parsing utilities for property files
"""
import pandas as pd
import re
import os
from pathlib import Path
from typing import Optional, List
from logger import setup_logger

logger = setup_logger(__name__)

# Input folder path
INPUT_FOLDER = "input"


def load_excel_file(file_path: str) -> pd.DataFrame:
    """
    Load an Excel file into a pandas DataFrame.
    Looks in the 'input' folder if the path is relative.
    
    Args:
        file_path: Path to the Excel file (relative or absolute)
        
    Returns:
        DataFrame containing the property data
    """
    try:
        # If path is not absolute, check in input folder
        if not os.path.isabs(file_path):
            # Check if input folder exists and file is there
            input_path = os.path.join(INPUT_FOLDER, file_path)
            if os.path.exists(input_path):
                file_path = input_path
            elif not os.path.exists(file_path):
                # Try input folder as fallback
                file_path = input_path
        
        df = pd.read_excel(file_path, engine='openpyxl')
        logger.info(f"Loaded {len(df)} rows from {file_path}")
        return df
    except Exception as e:
        logger.error(f"Error loading file {file_path}: {str(e)}")
        raise


def parse_price_range(price_str: str) -> Optional[float]:
    """
    Parse a price string that may be a range like "$270K - $305K" or single value.
    Returns the median if it's a range, or the value if it's a single price.
    
    Args:
        price_str: Price string (e.g., "$270K - $305K", "$300K", "$300,000")
        
    Returns:
        Parsed price as float, or None if parsing fails
    """
    if pd.isna(price_str) or not isinstance(price_str, str):
        return None
    
    try:
        # Remove whitespace
        price_str = price_str.strip()
        
        # Extract all dollar values using regex
        # Pattern matches: $300K, $300,000, $300K - $305K, etc.
        pattern = r'\$[\d,]+[KMB]?'
        matches = re.findall(pattern, price_str, re.IGNORECASE)
        
        if not matches:
            return None
        
        values = []
        for match in matches:
            # Remove $ and commas
            clean_match = match.replace('$', '').replace(',', '').upper()
            
            # Handle K, M, B suffixes
            multiplier = 1
            if clean_match.endswith('K'):
                multiplier = 1000
                clean_match = clean_match[:-1]
            elif clean_match.endswith('M'):
                multiplier = 1000000
                clean_match = clean_match[:-1]
            elif clean_match.endswith('B'):
                multiplier = 1000000000
                clean_match = clean_match[:-1]
            
            try:
                value = float(clean_match) * multiplier
                values.append(value)
            except ValueError:
                continue
        
        if not values:
            return None
        
        # Return median if multiple values, otherwise the single value
        if len(values) == 1:
            return values[0]
        else:
            return sum(values) / len(values)  # Average for range
        
    except Exception as e:
        logger.debug(f"Error parsing price '{price_str}': {str(e)}")
        return None


def extract_asking_price(display_price: str) -> Optional[float]:
    """
    Extract asking price from Display Price column if it contains "Asking price".
    
    Args:
        display_price: Display Price string
        
    Returns:
        Extracted asking price as float, or None if not found or doesn't contain "Asking price"
    """
    if pd.isna(display_price) or not isinstance(display_price, str):
        return None
    
    display_price_lower = display_price.lower()
    if "asking price" not in display_price_lower:
        return None
    
    # Extract price value
    return parse_price_range(display_price)


def extract_nearby_property_prices(nearby_properties: str) -> List[float]:
    """
    Extract dollar values from Nearby Properties column.
    The column contains property listings with prices in format like:
    "28 Abbott Street, Pareora ;; 2025-10-07 ;; $280,000 ;; https://..."
    
    Args:
        nearby_properties: Nearby Properties string
        
    Returns:
        List of extracted prices as floats
    """
    if pd.isna(nearby_properties) or not isinstance(nearby_properties, str):
        return []
    
    prices = []
    try:
        # Split by newlines to get individual property entries
        entries = nearby_properties.split('\n')
        
        for entry in entries:
            # Each entry has format: "Address ;; Date ;; Price ;; URL"
            # Extract price part (between second and third ;;)
            parts = entry.split(';;')
            if len(parts) >= 3:
                price_str = parts[2].strip()
                price = parse_price_range(price_str)
                if price is not None:
                    prices.append(price)
        
    except Exception as e:
        logger.debug(f"Error parsing nearby properties: {str(e)}")
    
    return prices


def calculate_median_price(prices: List[float]) -> Optional[float]:
    """
    Calculate median of a list of prices.
    
    Args:
        prices: List of price values
        
    Returns:
        Median price, or None if list is empty
    """
    if not prices:
        return None
    
    sorted_prices = sorted(prices)
    n = len(sorted_prices)
    
    if n % 2 == 0:
        # Even number of elements - average of two middle values
        return (sorted_prices[n // 2 - 1] + sorted_prices[n // 2]) / 2
    else:
        # Odd number of elements - middle value
        return sorted_prices[n // 2]


def parse_estimated_market_prices(df: pd.DataFrame) -> pd.Series:
    """
    Parse Estimated Market Price column and return a Series of parsed prices.
    
    Args:
        df: DataFrame with Estimated Market Price column
        
    Returns:
        Series of parsed prices (median for ranges)
    """
    if 'Estimated Market Price' not in df.columns:
        logger.warning("'Estimated Market Price' column not found")
        return pd.Series([None] * len(df))
    
    return df['Estimated Market Price'].apply(parse_price_range)


def prepare_property_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare property data by parsing price columns and extracting values.
    Adds new columns with parsed data.
    
    Args:
        df: Raw DataFrame from Excel file
        
    Returns:
        DataFrame with additional parsed columns
    """
    df = df.copy()
    
    # Parse Estimated Market Price
    df['Parsed_Estimated_Market_Price'] = parse_estimated_market_prices(df)
    
    # Extract asking price from Display Price
    if 'Display Price' in df.columns:
        df['Extracted_Asking_Price'] = df['Display Price'].apply(extract_asking_price)
    else:
        df['Extracted_Asking_Price'] = None
        logger.warning("'Display Price' column not found")
    
    # Extract nearby property prices
    if 'Nearby Properties' in df.columns:
        df['Nearby_Property_Prices'] = df['Nearby Properties'].apply(extract_nearby_property_prices)
    else:
        df['Nearby_Property_Prices'] = None
        logger.warning("'Nearby Properties' column not found")
    
    return df

