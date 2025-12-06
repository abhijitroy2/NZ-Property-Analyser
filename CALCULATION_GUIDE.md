# NZ Property Analyser - Calculation Guide & Results Interpretation

## Overview

The NZ Property Analyser evaluates properties using two distinct calculation modes: **Flip Mode** and **Rental Mode**. This guide explains how each calculation works and how to interpret the results in the generated Excel spreadsheets.

---

## Flip Mode Calculations

### Purpose
Flip Mode evaluates properties for short-term buy, renovate, and sell opportunities.

### Calculation Steps

#### 1. Potential Purchase Price
- **Primary Source**: Extracted from "Display Price" field if it contains "Asking price"
- **Fallback**: Uses median value from "Estimated Market Price" field
- This represents the expected purchase price for the property

#### 2. Potential Sale Price
- Calculated as the **median** of nearby property sale prices
- Extracted from the "Nearby Properties" field in the input data
- Represents the expected resale value after renovation

#### 3. Renovation Budget
- **Formula**: 15% of Potential Purchase Price
- Example: If purchase price is $300,000, renovation budget = $45,000

#### 4. Holding Costs
- **Formula**: 2.5% of Potential Purchase Price
- Covers costs like rates, utilities, and maintenance during the renovation period
- Example: If purchase price is $300,000, holding costs = $7,500

#### 5. Disposal Costs
- **Formula**: 3% of Potential Sale Price
- Includes real estate agent fees, legal costs, and other selling expenses
- Example: If sale price is $400,000, disposal costs = $12,000

#### 6. Contingency
- **Formula**: 1.5% of Renovation Budget
- Safety buffer for unexpected costs
- Example: If renovation budget is $45,000, contingency = $675

#### 7. Total Costs
- **Formula**: Purchase Price + Renovation + Holding Costs + Disposal Costs + Contingency
- Represents the total investment required

#### 8. Profit
- **Formula**: Potential Sale Price - Total Costs
- The expected profit from the flip

#### 9. ROI (Return on Investment)
- **Formula**: (Profit / Potential Purchase Price) × 100
- Measures return relative to purchase price
- Example: If profit is $60,000 and purchase price is $300,000, ROI = 20%

#### 10. Cash on Cash ROI
- **Formula**: (Profit / Total Cash Invested) × 100
- **Total Cash Invested** = 30% Down Payment + Renovation + Holding Costs + Disposal Costs
- Measures return on actual cash outlay (accounts for financing)
- Example: If profit is $60,000 and cash invested is $150,000, Cash on Cash ROI = 40%

### Good Deal Criteria (Flip Mode)
A property is marked as a **Good Deal** if:
- **ROI > 20%** OR
- **Cash on Cash ROI > 20%**

Properties meeting these criteria are:
- Highlighted in **green** in the Excel spreadsheet
- Included in the "Good Deals" sheet

---

## Rental Mode Calculations

### Purpose
Rental Mode evaluates properties for long-term rental investment opportunities.

### Calculation Steps

#### 1. Potential Purchase Price
- Same calculation as Flip Mode
- Extracted from "Display Price" or "Estimated Market Price"

#### 2. Weekly Rent
- Retrieved from rental data database based on the property's **District**
- Uses the **Geometric Mean** (upper quartile) rent for that district
- Represents expected weekly rental income

#### 3. Annual Rent
- **Formula**: Weekly Rent × 51 weeks
- Accounts for potential vacancy periods

#### 4. Gross Yield
- **Formula**: (Annual Rent / Potential Purchase Price) × 100
- Initial screening metric
- **If Gross Yield < 5%**: Calculation stops (property not viable)

#### 5. Outgoings Calculation
If Gross Yield ≥ 5%, the following outgoings are calculated:

##### 5a. Interest
- **Formula**: 5% of Purchase Price (or Adjusted Price if renovation project)
- Represents annual mortgage interest costs

##### 5b. Insurance
- Fetched from insurance API when possible
- Defaults to $2,000/year if unavailable

##### 5c. Accounting
- **Formula**: $2,100/year (fixed cost)

##### 5d. Body Corporate
- Extracted from property data if applicable
- Defaults to $0 if not applicable

##### 5e. Repairs
- **Formula**: $1,500/year (fixed maintenance allowance)

##### 5f. Total Outgoings
- **Formula**: Sum of all above outgoings
- Also calculated as weekly amount (Total Outgoings Annual / 51)

#### 6. Adjusted Purchase Price (Renovation Projects)
- If property description contains renovation keywords ("project", "renovation", "do-up", etc.)
- **Adjusted Price** = Purchase Price + $30,000
- Used for yield calculations to account for additional investment

#### 7. Weekly Net Rent
- **Formula**: Weekly Rent - Weekly Outgoings
- Actual cash flow per week

#### 8. Annual Net Rent (Net Income)
- **Formula**: Weekly Net Rent × 51 weeks
- Annual cash flow after all expenses
- Also called "Net Income/Loss"

#### 9. Net Yield
- **Formula**: (Annual Net Rent / Adjusted Purchase Price) × 100
- Uses Adjusted Price if renovation project, otherwise uses Purchase Price
- Key metric for rental viability

### Success Criteria (Rental Mode)
A property is marked as **Successful** if:
- **Net Yield > 4%** AND
- **Net Annual Income > -$5,000**

Properties meeting these criteria are:
- Highlighted in **green** in the Excel spreadsheet
- Included in the "Good Deals" sheet

---

## Understanding the Excel Spreadsheet

### Sheet Structure

#### 1. Summary Sheet
- Contains **all properties** with complete calculations
- **Green highlighting**: Good deals (meets success criteria)
- **Yellow highlighting**: Properties with stress keywords (motivated sellers)
- Use this sheet for comprehensive analysis

#### 2. Good Deals Sheet
- Contains only properties that meet success criteria
- **Flip Mode**: Properties with ROI > 20% OR Cash on Cash ROI > 20%
- **Rental Mode**: Properties with Net Yield > 4% AND Net Income > -$5,000
- All rows highlighted in green
- Quick reference for best opportunities

#### 3. Stress Sales Sheet
- Contains properties with stress keywords in descriptions
- Keywords include: "urgent", "must sell", "motivated", "quick sale", "price reduced", etc.
- All rows highlighted in yellow
- May indicate motivated sellers and negotiation opportunities

#### 4. Metadata Sheet
- Contains processing information and configuration values
- Useful for understanding calculation parameters

### Key Columns to Review

#### Flip Mode Columns
- **Potential_Purchase_Price**: Expected purchase price
- **Potential_Sale_Price**: Expected resale price
- **Profit**: Expected profit ($)
- **ROI_Percent**: Return on investment percentage
- **Cash_on_Cash_ROI_Percent**: Return on cash invested percentage
- **Is_Good_Deal**: TRUE if meets criteria

#### Rental Mode Columns
- **Potential_Purchase_Price**: Expected purchase price
- **Weekly_Rent**: Expected weekly rental income
- **Annual_Rent**: Expected annual rental income
- **Gross_Yield_Percent**: Gross yield percentage
- **Net_Yield_Percent**: Net yield after expenses
- **Net_Income_Loss**: Annual cash flow ($)
- **Is_Successful**: TRUE if meets criteria

### Color Coding
- **Green**: Good deals / Successful properties
- **Yellow**: Stress sales (motivated sellers)
- **Blue Header**: Column headers
- **White**: Standard properties

---

## Important Notes

### Data Quality
- Properties with missing critical data (purchase price, sale price, district) will show calculation errors
- Check the "Calculation_Errors" column for issues

### Assumptions
- **Flip Mode**: Assumes standard renovation scope (15% of purchase price)
- **Rental Mode**: Uses district-level rental data (may not reflect exact property)
- Insurance costs default to $2,000/year if API unavailable
- Interest rate fixed at 5% annually

### Limitations
- Calculations are estimates based on available data
- Actual results may vary based on:
  - Actual renovation costs
  - Market conditions
  - Rental market fluctuations
  - Interest rate changes
  - Property-specific factors

### Best Practices
1. Review "Good Deals" sheet first for quick opportunities
2. Cross-reference with "Summary" sheet for full context
3. Check "Stress Sales" for potential negotiation leverage
4. Verify property addresses and URLs before proceeding
5. Consider additional factors not captured in calculations:
   - Location desirability
   - Property condition
   - Market trends
   - Personal investment goals

---

## Executive Summary

The Executive Summary Excel file consolidates all "Good Deals" from multiple analysis runs into two tabs:
- **Good Deals - Flip**: All flip opportunities across all processed files
- **Good Deals - Rental**: All rental opportunities across all processed files

This provides a single view of the best opportunities from your entire analysis batch.

---

*Last Updated: December 2025*

