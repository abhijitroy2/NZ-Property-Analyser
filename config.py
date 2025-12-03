"""
Configuration constants for NZ Property Analyser
"""

# Default email for background mode
DEFAULT_EMAIL = "abbey.roy@gmail.com"

# Stress keywords for detecting sale stress indicators
STRESS_KEYWORDS = [
    "urgent",
    "must sell",
    "motivated",
    "quick sale",
    "price reduced",
    "below market",
    "distressed",
    "foreclosure",
    "bank sale",
    "mortgagee",
    "motivated seller",
    "urgent sale",
    "price drop",
    "reduced price"
]

# Flip calculator percentages
RENOVATION_BUDGET_PERCENT = 0.15  # 15% of Potential Purchase Price
HOLDING_COSTS_PERCENT = 0.025  # 2.5% of Potential Purchase Price
DISPOSAL_COSTS_PERCENT = 0.03  # 3% of Potential Sale Price
CONTINGENCY_PERCENT = 0.015  # 1.5% of Renovation Budget
CASH_ON_CASH_DOWN_PAYMENT_PERCENT = 0.30  # 30% of Potential Purchase Price

# Rental calculator constants
WEEKS_PER_YEAR = 51
OUTGOINGS_MULTIPLIER = 1.15  # Outgoings = Holding Costs * 1.15

# Thresholds
FLIP_ROI_THRESHOLD = 0.20  # 20% ROI threshold for good deals
RENTAL_GROSS_YIELD_THRESHOLD = 0.05  # 5% Gross Yield threshold
RENTAL_NET_YIELD_THRESHOLD = 0.04  # 4% Net Yield threshold
RENTAL_NET_INCOME_THRESHOLD = -5000  # -$5000 minimum Net Annual Income

# File paths
RENTAL_DATA_FILE = "Detailed-Monthly-TLA-Tenancy-v2.csv"
LOG_FILE = "property_analyser.log"

