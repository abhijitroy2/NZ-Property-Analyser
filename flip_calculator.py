"""
Flip calculator for property investment analysis
"""
from typing import Optional, Dict
import pandas as pd
from data_loader import (
    extract_asking_price,
    parse_price_range,
    calculate_median_price,
    extract_nearby_property_prices
)
from config import (
    RENOVATION_BUDGET_PERCENT,
    HOLDING_COSTS_PERCENT,
    DISPOSAL_COSTS_PERCENT,
    CONTINGENCY_PERCENT,
    CASH_ON_CASH_DOWN_PAYMENT_PERCENT,
    FLIP_ROI_THRESHOLD
)
from logger import setup_logger

logger = setup_logger(__name__)


def calculate_potential_purchase_price(row: pd.Series) -> Optional[float]:
    """
    Calculate Potential Purchase Price.
    If Display Price contains "Asking price", use that.
    Otherwise, use median of Estimated Market Price values.
    
    Args:
        row: Property row from DataFrame
        
    Returns:
        Potential Purchase Price, or None if cannot be determined
    """
    # First try to extract asking price from Display Price
    if 'Display Price' in row and pd.notna(row.get('Display Price')):
        asking_price = extract_asking_price(row['Display Price'])
        if asking_price is not None:
            logger.debug(f"Using asking price: ${asking_price:,.2f}")
            return asking_price
    
    # Otherwise, use median of Estimated Market Price
    if 'Parsed_Estimated_Market_Price' in row and pd.notna(row.get('Parsed_Estimated_Market_Price')):
        estimated_price = row['Parsed_Estimated_Market_Price']
        logger.debug(f"Using estimated market price: ${estimated_price:,.2f}")
        return estimated_price
    
    # If we have the raw Estimated Market Price column, try parsing it
    if 'Estimated Market Price' in row and pd.notna(row.get('Estimated Market Price')):
        estimated_price = parse_price_range(row['Estimated Market Price'])
        if estimated_price is not None:
            logger.debug(f"Parsed estimated market price: ${estimated_price:,.2f}")
            return estimated_price
    
    logger.warning("Could not determine Potential Purchase Price")
    return None


def calculate_potential_sale_price(row: pd.Series) -> Optional[float]:
    """
    Calculate Potential Sale Price as median of nearby property prices.
    
    Args:
        row: Property row from DataFrame
        
    Returns:
        Potential Sale Price (median of nearby properties), or None if cannot be determined
    """
    if 'Nearby_Property_Prices' in row:
        nearby_prices = row['Nearby_Property_Prices']
        if isinstance(nearby_prices, list) and nearby_prices:
            median_price = calculate_median_price(nearby_prices)
            if median_price is not None:
                logger.debug(f"Potential Sale Price (median of {len(nearby_prices)} nearby properties): ${median_price:,.2f}")
                return median_price
    
    # Try extracting from raw Nearby Properties column
    if 'Nearby Properties' in row and pd.notna(row.get('Nearby Properties')):
        nearby_prices = extract_nearby_property_prices(row['Nearby Properties'])
        if nearby_prices:
            median_price = calculate_median_price(nearby_prices)
            if median_price is not None:
                logger.debug(f"Potential Sale Price (median of {len(nearby_prices)} nearby properties): ${median_price:,.2f}")
                return median_price
    
    logger.warning("Could not determine Potential Sale Price - no nearby property data")
    return None


def calculate_flip_metrics(row: pd.Series) -> Dict:
    """
    Calculate all flip metrics for a property.
    
    Args:
        row: Property row from DataFrame
        
    Returns:
        Dictionary containing all calculated metrics
    """
    metrics = {
        'Potential_Purchase_Price': None,
        'Renovation_Budget': None,
        'Holding_Costs': None,
        'Disposal_Costs': None,
        'Contingency': None,
        'Potential_Sale_Price': None,
        'Total_Costs': None,
        'Profit': None,
        'ROI_Percent': None,
        'Cash_on_Cash_ROI_Percent': None,
        'Is_Good_Deal': False,
        'Calculation_Errors': []
    }
    
    try:
        # Calculate Potential Purchase Price
        potential_purchase_price = calculate_potential_purchase_price(row)
        if potential_purchase_price is None:
            metrics['Calculation_Errors'].append("Potential Purchase Price")
            return metrics
        metrics['Potential_Purchase_Price'] = potential_purchase_price
        
        # Calculate Potential Sale Price
        potential_sale_price = calculate_potential_sale_price(row)
        if potential_sale_price is None:
            metrics['Calculation_Errors'].append("Potential Sale Price")
            return metrics
        metrics['Potential_Sale_Price'] = potential_sale_price
        
        # Calculate Renovation Budget (15% of Potential Purchase Price)
        renovation_budget = potential_purchase_price * RENOVATION_BUDGET_PERCENT
        metrics['Renovation_Budget'] = renovation_budget
        logger.debug(f"Renovation Budget: ${renovation_budget:,.2f}")
        
        # Calculate Holding Costs (2.5% of Potential Purchase Price)
        holding_costs = potential_purchase_price * HOLDING_COSTS_PERCENT
        metrics['Holding_Costs'] = holding_costs
        logger.debug(f"Holding Costs: ${holding_costs:,.2f}")
        
        # Calculate Disposal Costs (3% of Potential Sale Price)
        disposal_costs = potential_sale_price * DISPOSAL_COSTS_PERCENT
        metrics['Disposal_Costs'] = disposal_costs
        logger.debug(f"Disposal Costs: ${disposal_costs:,.2f}")
        
        # Calculate Contingency (1.5% of Renovation Budget)
        contingency = renovation_budget * CONTINGENCY_PERCENT
        metrics['Contingency'] = contingency
        logger.debug(f"Contingency: ${contingency:,.2f}")
        
        # Calculate Total Costs
        total_costs = (
            potential_purchase_price +
            renovation_budget +
            holding_costs +
            disposal_costs +
            contingency
        )
        metrics['Total_Costs'] = total_costs
        
        # Calculate Profit
        # Note: Following the plan's interpretation: Profit = Sale Price - Total Costs
        profit = potential_sale_price - total_costs
        metrics['Profit'] = profit
        logger.debug(f"Profit: ${profit:,.2f}")
        
        # Calculate ROI % (Profit / Potential Purchase Price)
        if potential_purchase_price > 0:
            roi_percent = (profit / potential_purchase_price) * 100
            metrics['ROI_Percent'] = roi_percent
            logger.debug(f"ROI %: {roi_percent:.2f}%")
        
        # Calculate Cash on Cash ROI
        # Cash on Cash ROI = Profit / (30% of Potential Purchase Price + Renovation + Holding Cost + Disposal Cost)
        down_payment = potential_purchase_price * CASH_ON_CASH_DOWN_PAYMENT_PERCENT
        total_cash_invested = down_payment + renovation_budget + holding_costs + disposal_costs
        
        if total_cash_invested > 0:
            cash_on_cash_roi_percent = (profit / total_cash_invested) * 100
            metrics['Cash_on_Cash_ROI_Percent'] = cash_on_cash_roi_percent
            logger.debug(f"Cash on Cash ROI %: {cash_on_cash_roi_percent:.2f}%")
        
        # Determine if it's a good deal
        # Good deal if ROI > 20% OR Cash on Cash ROI > 20%
        is_good_deal = False
        if metrics['ROI_Percent'] is not None and metrics['ROI_Percent'] > (FLIP_ROI_THRESHOLD * 100):
            is_good_deal = True
        elif metrics['Cash_on_Cash_ROI_Percent'] is not None and metrics['Cash_on_Cash_ROI_Percent'] > (FLIP_ROI_THRESHOLD * 100):
            is_good_deal = True
        
        metrics['Is_Good_Deal'] = is_good_deal
        
        if is_good_deal:
            logger.info(f"Property identified as good deal - ROI: {metrics['ROI_Percent']:.2f}%, "
                       f"Cash on Cash ROI: {metrics['Cash_on_Cash_ROI_Percent']:.2f}%")
        
    except Exception as e:
        logger.error(f"Error calculating flip metrics: {str(e)}")
        metrics['Calculation_Errors'].append(f"General error: {str(e)}")
    
    return metrics

