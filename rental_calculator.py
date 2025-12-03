"""
Rental calculator for property investment analysis
"""
from typing import Optional, Dict
import pandas as pd
from rental_data_loader import get_upper_quartile_rent
from flip_calculator import calculate_potential_purchase_price
from config import (
    WEEKS_PER_YEAR,
    OUTGOINGS_MULTIPLIER,
    HOLDING_COSTS_PERCENT,
    RENTAL_GROSS_YIELD_THRESHOLD,
    RENTAL_NET_YIELD_THRESHOLD,
    RENTAL_NET_INCOME_THRESHOLD
)
from logger import setup_logger

logger = setup_logger(__name__)


def calculate_rental_metrics(row: pd.Series) -> Dict:
    """
    Calculate all rental metrics for a property.
    
    Args:
        row: Property row from DataFrame
        
    Returns:
        Dictionary containing all calculated metrics
    """
    metrics = {
        'Potential_Purchase_Price': None,
        'Weekly_Rent': None,
        'Annual_Rent': None,
        'Gross_Yield_Percent': None,
        'Gross_Yield_Below_Threshold': False,
        'Holding_Costs': None,
        'Outgoings': None,
        'Weekly_Net_Rent': None,
        'Annual_Net_Rent': None,
        'Net_Yield_Percent': None,
        'Net_Income_Loss': None,
        'Is_Successful': False,
        'Calculation_Errors': []
    }
    
    try:
        # Get Potential Purchase Price (same as flip calculator)
        potential_purchase_price = calculate_potential_purchase_price(row)
        if potential_purchase_price is None:
            metrics['Calculation_Errors'].append("Potential Purchase Price")
            return metrics
        metrics['Potential_Purchase_Price'] = potential_purchase_price
        
        # Get District from row
        district = None
        if 'District' in row and pd.notna(row.get('District')):
            district = row['District']
        else:
            metrics['Calculation_Errors'].append("District")
            logger.warning("District not found in property data")
            return metrics
        
        # Get Weekly Rent from rental data (Upper Quartile Rent)
        weekly_rent = get_upper_quartile_rent(district)
        if weekly_rent is None:
            metrics['Calculation_Errors'].append("Weekly Rent (District not found in rental data)")
            logger.warning(f"Could not find rental data for district: {district}")
            return metrics
        metrics['Weekly_Rent'] = weekly_rent
        logger.debug(f"Weekly Rent (Upper Quartile) for {district}: ${weekly_rent:.2f}")
        
        # Calculate Annual Rent (Weekly Rent × 51)
        annual_rent = weekly_rent * WEEKS_PER_YEAR
        metrics['Annual_Rent'] = annual_rent
        logger.debug(f"Annual Rent: ${annual_rent:,.2f}")
        
        # Calculate Gross Yield (Annual Rent / Potential Purchase Price)
        if potential_purchase_price > 0:
            gross_yield_percent = (annual_rent / potential_purchase_price) * 100
            metrics['Gross_Yield_Percent'] = gross_yield_percent
            logger.debug(f"Gross Yield: {gross_yield_percent:.2f}%")
            
            # Check if Gross Yield < 5% (threshold)
            if gross_yield_percent < (RENTAL_GROSS_YIELD_THRESHOLD * 100):
                metrics['Gross_Yield_Below_Threshold'] = True
                logger.info(f"Gross Yield {gross_yield_percent:.2f}% is below 5% threshold - stopping calculation")
                return metrics
        
        # Calculate Holding Costs (2.5% of Potential Purchase Price) - annual
        holding_costs_annual = potential_purchase_price * HOLDING_COSTS_PERCENT
        metrics['Holding_Costs'] = holding_costs_annual
        logger.debug(f"Holding Costs (annual): ${holding_costs_annual:,.2f}")
        
        # Calculate weekly holding costs
        holding_costs_weekly = holding_costs_annual / 52
        
        # Calculate Outgoings (weekly) = Holding Costs (weekly) × 1.15
        outgoings_weekly = holding_costs_weekly * OUTGOINGS_MULTIPLIER
        metrics['Outgoings'] = outgoings_weekly
        logger.debug(f"Outgoings (weekly): ${outgoings_weekly:,.2f}")
        
        # Calculate Weekly Net Rent (Weekly Rent - Outgoings)
        weekly_net_rent = weekly_rent - outgoings_weekly
        metrics['Weekly_Net_Rent'] = weekly_net_rent
        logger.debug(f"Weekly Net Rent: ${weekly_net_rent:,.2f}")
        
        # Calculate Annual Net Rent (Weekly Net Rent × 51)
        annual_net_rent = weekly_net_rent * WEEKS_PER_YEAR
        metrics['Annual_Net_Rent'] = annual_net_rent
        metrics['Net_Income_Loss'] = annual_net_rent  # Same value, different name
        logger.debug(f"Annual Net Rent: ${annual_net_rent:,.2f}")
        
        # Calculate Net Yield (Annual Net Rent / Potential Purchase Price)
        if potential_purchase_price > 0:
            net_yield_percent = (annual_net_rent / potential_purchase_price) * 100
            metrics['Net_Yield_Percent'] = net_yield_percent
            logger.debug(f"Net Yield: {net_yield_percent:.2f}%")
        
        # Determine success criteria
        # Success: Net Yield > 4% AND Net Annual Income > -$5000
        is_successful = False
        if (metrics['Net_Yield_Percent'] is not None and 
            metrics['Net_Yield_Percent'] > (RENTAL_NET_YIELD_THRESHOLD * 100) and
            metrics['Net_Income_Loss'] > RENTAL_NET_INCOME_THRESHOLD):
            is_successful = True
        
        metrics['Is_Successful'] = is_successful
        
        if is_successful:
            logger.info(f"Property meets success criteria - Net Yield: {metrics['Net_Yield_Percent']:.2f}%, "
                       f"Net Income: ${metrics['Net_Income_Loss']:,.2f}")
        
    except Exception as e:
        logger.error(f"Error calculating rental metrics: {str(e)}")
        metrics['Calculation_Errors'].append(f"General error: {str(e)}")
    
    return metrics

