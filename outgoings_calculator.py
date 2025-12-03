"""
Outgoings calculator for rental properties
"""
import re
from typing import Dict, Optional
import pandas as pd
from insurance_fetcher import get_insurance_cost
from logger import setup_logger

logger = setup_logger(__name__)

# Constants
INTEREST_RATE = 0.05  # 5% annual
ACCOUNTING_MONTHLY = 175
ACCOUNTING_ANNUAL = ACCOUNTING_MONTHLY * 12  # $2,100/year
DEFAULT_INSURANCE_ANNUAL = 2000
RENOVATION_REPAIRS_ANNUAL = 1500
STANDARD_REPAIRS_ANNUAL = 500
RENOVATION_PRICE_ADJUSTMENT = 30000  # Add $30k to purchase price if renovation

# Renovation keywords
RENOVATION_KEYWORDS = [
    "renovation",
    "renovate",
    "fixer upper",
    "needs work",
    "do up",
    "as is",
    "needs updating",
    "needs repair",
    "needs attention",
    "project",
    "potential",
    "tlc",
    "tender loving care",
    "handyman special",
    "needs tlc"
]


def detect_renovation_project(row: pd.Series) -> bool:
    """
    Detect if property is a renovation project by checking title and description.
    
    Args:
        row: Property row from DataFrame
        
    Returns:
        True if renovation project detected, False otherwise
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
    
    # Check for renovation keywords (case-insensitive)
    for keyword in RENOVATION_KEYWORDS:
        if keyword.lower() in combined_text:
            logger.debug(f"Renovation keyword '{keyword}' found in property")
            return True
    
    return False


def extract_body_corporate_cost(description: str) -> float:
    """
    Extract Body Corporate cost from Description using regex.
    Looks for "body corporate" followed by a dollar amount.
    
    Args:
        description: Property description text
        
    Returns:
        Annual Body Corporate cost, or 0 if not found
    """
    if pd.isna(description) or not isinstance(description, str):
        return 0.0
    
    description_lower = description.lower()
    
    # Check if "body corporate" is mentioned
    if "body corporate" not in description_lower:
        return 0.0
    
    # Try to find dollar amounts near "body corporate"
    # Pattern: "body corporate" followed by optional text and then $amount
    # Or $amount followed by "body corporate"
    patterns = [
        r'body corporate[^$]*\$[\d,]+\.?\d*',  # "body corporate ... $500"
        r'\$[\d,]+\.?\d*[^$]*body corporate',  # "$500 ... body corporate"
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, description_lower, re.IGNORECASE)
        if matches:
            # Extract the dollar amount
            for match in matches:
                # Extract number after $
                amount_str = re.search(r'\$[\d,]+\.?\d*', match)
                if amount_str:
                    amount = amount_str.group().replace('$', '').replace(',', '')
                    try:
                        value = float(amount)
                        logger.debug(f"Found Body Corporate amount: ${value:,.2f}")
                        
                        # Check if it's monthly/quarterly and convert to annual
                        # Look in the surrounding context (within 50 chars of the match)
                        match_start = description_lower.find(match)
                        context = description_lower[max(0, match_start-50):match_start+len(match)+50]
                        
                        if 'per month' in context or '/month' in context or 'monthly' in context:
                            annual_value = value * 12
                            logger.debug(f"Converting monthly ${value:,.2f} to annual ${annual_value:,.2f}")
                            return annual_value
                        elif 'per quarter' in context or '/quarter' in context or 'quarterly' in context:
                            annual_value = value * 4
                            logger.debug(f"Converting quarterly ${value:,.2f} to annual ${annual_value:,.2f}")
                            return annual_value
                        elif 'per week' in context or '/week' in context or 'weekly' in context:
                            annual_value = value * 52
                            logger.debug(f"Converting weekly ${value:,.2f} to annual ${annual_value:,.2f}")
                            return annual_value
                        else:
                            # Assume annual
                            logger.debug(f"Assuming annual Body Corporate: ${value:,.2f}")
                            return value
                    except ValueError:
                        continue
    
    logger.debug("Body Corporate mentioned but no amount found, using $0")
    return 0.0


def calculate_outgoings(row: pd.Series, potential_purchase_price: float) -> Dict:
    """
    Calculate all outgoings components for a rental property.
    
    Outgoings = Interest + Insurance + Accounting + Body Corporate + Repairs
    
    Args:
        row: Property row from DataFrame
        potential_purchase_price: Purchase price (may be adjusted for renovations)
        
    Returns:
        Dictionary with all outgoings components and total
    """
    outgoings = {
        'Interest': None,
        'Insurance': None,
        'Accounting': None,
        'Body_Corporate': None,
        'Repairs': None,
        'Total_Outgoings_Annual': None,
        'Total_Outgoings_Weekly': None,
        'Is_Renovation_Project': False,
        'Adjusted_Purchase_Price': potential_purchase_price
    }
    
    # Detect if renovation project
    is_renovation = detect_renovation_project(row)
    outgoings['Is_Renovation_Project'] = is_renovation
    
    # Adjust purchase price if renovation (affects interest calculation)
    adjusted_price = potential_purchase_price
    if is_renovation:
        adjusted_price = potential_purchase_price + RENOVATION_PRICE_ADJUSTMENT
        outgoings['Adjusted_Purchase_Price'] = adjusted_price
        logger.debug(f"Renovation project detected - adjusting purchase price from ${potential_purchase_price:,.2f} to ${adjusted_price:,.2f}")
    
    # 1. Interest = 5% of Purchase Price (use adjusted price if renovation)
    interest_annual = adjusted_price * INTEREST_RATE
    outgoings['Interest'] = interest_annual
    logger.debug(f"Interest (5% of ${adjusted_price:,.2f}): ${interest_annual:,.2f}/year")
    
    # 2. Insurance - try to fetch, fallback to default
    address = row.get('Property Address', '') or row.get('Address', '')
    insurance_annual = get_insurance_cost(address)
    outgoings['Insurance'] = insurance_annual
    logger.debug(f"Insurance: ${insurance_annual:,.2f}/year")
    
    # 3. Accounting = $175/month = $2,100/year
    accounting_annual = ACCOUNTING_ANNUAL
    outgoings['Accounting'] = accounting_annual
    logger.debug(f"Accounting: ${accounting_annual:,.2f}/year")
    
    # 4. Body Corporate - extract from Description
    description = row.get('Description', '')
    body_corporate_annual = extract_body_corporate_cost(description)
    outgoings['Body_Corporate'] = body_corporate_annual
    logger.debug(f"Body Corporate: ${body_corporate_annual:,.2f}/year")
    
    # 5. Repairs - $1,500/year if renovation, else $500/year
    if is_renovation:
        repairs_annual = RENOVATION_REPAIRS_ANNUAL
    else:
        repairs_annual = STANDARD_REPAIRS_ANNUAL
    outgoings['Repairs'] = repairs_annual
    logger.debug(f"Repairs: ${repairs_annual:,.2f}/year")
    
    # Calculate total outgoings (annual)
    total_outgoings_annual = (
        interest_annual +
        insurance_annual +
        accounting_annual +
        body_corporate_annual +
        repairs_annual
    )
    outgoings['Total_Outgoings_Annual'] = total_outgoings_annual
    
    # Convert to weekly (divide by 51 weeks per year)
    from config import WEEKS_PER_YEAR
    total_outgoings_weekly = total_outgoings_annual / WEEKS_PER_YEAR
    outgoings['Total_Outgoings_Weekly'] = total_outgoings_weekly
    
    logger.debug(f"Total Outgoings (annual): ${total_outgoings_annual:,.2f}")
    logger.debug(f"Total Outgoings (weekly): ${total_outgoings_weekly:,.2f}")
    
    return outgoings

