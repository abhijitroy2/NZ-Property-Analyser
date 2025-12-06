"""
Extract good deals information from Executive Summary for email body
"""
import pandas as pd
import sys
import os

def extract_good_deals_info(executive_summary_path: str) -> str:
    """
    Extract good deals information and format for email body.
    
    Args:
        executive_summary_path: Path to Executive Summary Excel file
        
    Returns:
        Formatted string with good deals information
    """
    if not os.path.exists(executive_summary_path):
        return "No Executive Summary available.\n"
    
    try:
        output_lines = []
        output_lines.append("GOOD DEALS SUMMARY")
        output_lines.append("=" * 60)
        output_lines.append("")
        
        # Read flip deals
        try:
            flip_df = pd.read_excel(executive_summary_path, sheet_name='Good Deals - Flip')
            if not flip_df.empty:
                output_lines.append("FLIP GOOD DEALS:")
                output_lines.append("-" * 60)
                for i, (_, row) in enumerate(flip_df.iterrows(), 1):
                    address = row.get('Property Address', 'N/A')
                    url = row.get('URL', 'N/A')
                    purchase_price = row.get('Potential_Purchase_Price', 'N/A')
                    sale_price = row.get('Potential_Sale_Price', 'N/A')
                    profit = row.get('Profit', 'N/A')
                    roi = row.get('ROI_Percent', 'N/A')
                    cash_on_cash = row.get('Cash_on_Cash_ROI_Percent', 'N/A')
                    
                    if isinstance(purchase_price, (int, float)):
                        purchase_price = f"${purchase_price:,.0f}"
                    if isinstance(sale_price, (int, float)):
                        sale_price = f"${sale_price:,.0f}"
                    if isinstance(profit, (int, float)):
                        profit = f"${profit:,.0f}"
                    if isinstance(roi, (int, float)):
                        roi = f"{roi:.2f}%"
                    if isinstance(cash_on_cash, (int, float)):
                        cash_on_cash = f"{cash_on_cash:.2f}%"
                    
                    output_lines.append(f"{i}. {address}")
                    output_lines.append(f"   URL: {url}")
                    output_lines.append(f"   Purchase: {purchase_price} | Sale: {sale_price} | Profit: {profit}")
                    output_lines.append(f"   ROI: {roi} | Cash on Cash ROI: {cash_on_cash}")
                    output_lines.append("")
        except Exception as e:
            output_lines.append("No flip good deals found.")
            output_lines.append("")
        
        # Read rental deals
        try:
            rental_df = pd.read_excel(executive_summary_path, sheet_name='Good Deals - Rental')
            if not rental_df.empty:
                output_lines.append("RENTAL GOOD DEALS:")
                output_lines.append("-" * 60)
                for i, (_, row) in enumerate(rental_df.iterrows(), 1):
                    address = row.get('Property Address', 'N/A')
                    url = row.get('URL', 'N/A')
                    purchase_price = row.get('Potential_Purchase_Price', 'N/A')
                    weekly_rent = row.get('Weekly_Rent', 'N/A')
                    net_yield = row.get('Net_Yield_Percent', 'N/A')
                    net_income = row.get('Net_Income_Loss', 'N/A')
                    
                    if isinstance(purchase_price, (int, float)):
                        purchase_price = f"${purchase_price:,.0f}"
                    if isinstance(weekly_rent, (int, float)):
                        weekly_rent = f"${weekly_rent:.2f}/week"
                    if isinstance(net_yield, (int, float)):
                        net_yield = f"{net_yield:.2f}%"
                    if isinstance(net_income, (int, float)):
                        net_income = f"${net_income:,.0f}/year"
                    
                    output_lines.append(f"{i}. {address}")
                    output_lines.append(f"   URL: {url}")
                    output_lines.append(f"   Purchase: {purchase_price} | Weekly Rent: {weekly_rent}")
                    output_lines.append(f"   Net Yield: {net_yield} | Net Income: {net_income}")
                    output_lines.append("")
        except Exception as e:
            output_lines.append("No rental good deals found.")
            output_lines.append("")
        
        return "\n".join(output_lines)
        
    except Exception as e:
        return f"Error reading Executive Summary: {str(e)}\n"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_good_deals_info.py <executive_summary.xlsx>")
        sys.exit(1)
    
    executive_summary_path = sys.argv[1]
    result = extract_good_deals_info(executive_summary_path)
    print(result)

