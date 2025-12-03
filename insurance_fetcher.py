"""
Insurance quote fetcher from initio.co.nz
"""
import re
import requests
from typing import Optional
from logger import setup_logger

logger = setup_logger(__name__)

# Default insurance if fetch fails
DEFAULT_INSURANCE_ANNUAL = 2000


def fetch_insurance_quote(address: str) -> Optional[float]:
    """
    Attempt to fetch insurance quote from initio.co.nz website.
    This is a placeholder - actual implementation would need to:
    1. Navigate to initio.co.nz/get-quote
    2. Fill in address form
    3. Extract quote value
    
    Args:
        address: Property address
        
    Returns:
        Annual insurance cost, or None if fetch fails
    """
    try:
        # TODO: Implement actual web scraping or API call
        # For now, this is a placeholder that will always fail and use default
        logger.debug(f"Attempting to fetch insurance quote for: {address}")
        
        # Placeholder for future implementation
        # Would need to use selenium/playwright or check if API exists
        # For now, return None to use default
        
        return None
        
    except Exception as e:
        logger.warning(f"Error fetching insurance quote: {str(e)}")
        return None


def get_insurance_cost(address: str) -> float:
    """
    Get insurance cost for a property.
    Tries to fetch from initio.co.nz, falls back to default if fails.
    
    Args:
        address: Property address
        
    Returns:
        Annual insurance cost
    """
    quote = fetch_insurance_quote(address)
    
    if quote is not None:
        logger.info(f"Fetched insurance quote: ${quote:,.2f}/year for {address}")
        return quote
    else:
        logger.warning(f"Could not fetch insurance quote for {address}, using default ${DEFAULT_INSURANCE_ANNUAL}/year")
        return DEFAULT_INSURANCE_ANNUAL

