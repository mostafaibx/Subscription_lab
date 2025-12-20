"""
Shared utility functions for data generation.
Contains: ID generation, date helpers, proration math, timezone handling.
"""

from datetime import datetime, timedelta, date, timezone
from pathlib import Path
import yaml


# =============================================================================
# CONFIGURATION
# =============================================================================

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent


def load_config():
    """Load configuration from config.yml (relative to script location)."""
    config_path = SCRIPT_DIR / 'config.yml'
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


# Load config once at module level
CONFIG = load_config()

# Build PLANS dict keyed by plan_id for easy lookup
PLANS = {p['plan_id']: p for p in CONFIG['plans']}

# Timezone from config (default UTC)
TZ = timezone.utc


# =============================================================================
# TIMEZONE-AWARE DATETIME HELPERS
# =============================================================================

def to_utc(dt):
    """
    Convert a datetime to timezone-aware UTC.
    If already aware, returns as-is.
    If naive, assumes UTC.
    """
    if dt is None:
        return None
    if isinstance(dt, date) and not isinstance(dt, datetime):
        # Convert date to datetime at midnight UTC
        dt = datetime.combine(dt, datetime.min.time())
    if dt.tzinfo is None:
        return dt.replace(tzinfo=TZ)
    return dt


def utc_now():
    """Get current UTC datetime (timezone-aware)."""
    return datetime.now(TZ)


def utc_datetime(year, month, day, hour=0, minute=0, second=0):
    """Create a timezone-aware UTC datetime."""
    return datetime(year, month, day, hour, minute, second, tzinfo=TZ)


# =============================================================================
# ID GENERATION
# =============================================================================

def generate_id(prefix, counter, width=4):
    """
    Generate a formatted ID string.
    
    Examples:
        generate_id('CUST', 1) -> 'CUST_0001'
        generate_id('EVT', 42, width=6) -> 'EVT_000042'
    """
    return f"{prefix}_{counter:0{width}d}"


# =============================================================================
# DATE HELPERS
# =============================================================================

def add_days(dt, days):
    """
    Add days to a date or datetime.
    Returns a timezone-aware datetime.
    """
    if isinstance(dt, date) and not isinstance(dt, datetime):
        dt = datetime.combine(dt, datetime.min.time())
    result = dt + timedelta(days=days)
    return to_utc(result)


def get_term_days(billing_period_months, config=None):
    """
    Get term length in days based on billing period.
    Uses synthetic simplification: 30 days for monthly, 360 for annual.
    """
    if config is None:
        config = CONFIG
    
    if billing_period_months == 1:
        return config['monthly_term_days']  # 30
    elif billing_period_months == 12:
        return config['annual_term_days']   # 360
    # Fallback for other periods
    return billing_period_months * 30


def calculate_period_end(start_date, billing_period_months, config=None):
    """
    Calculate the period end date based on start date and billing period.
    
    Args:
        start_date: Start date (date or datetime)
        billing_period_months: 1 for monthly, 12 for annual
        config: Optional config dict (uses global CONFIG if None)
    
    Returns:
        date: Period end date
    """
    if config is None:
        config = CONFIG
    
    term_days = get_term_days(billing_period_months, config)
    end_dt = add_days(start_date, term_days)
    return end_dt.date()


def calculate_paid_at(issued_at, config=None, is_paid=True):
    """
    Calculate paid_at timestamp based on issued_at and pay delay settings.
    
    Args:
        issued_at: Invoice issued datetime
        config: Optional config dict
        is_paid: If False, returns None (for uncollectible invoices)
    
    Returns:
        datetime or None
    """
    if not is_paid:
        return None
    
    if config is None:
        config = CONFIG
    
    import numpy as np
    min_delay = config['invoices']['pay_delay_days_min']
    max_delay = config['invoices']['pay_delay_days_max']
    delay_days = np.random.randint(min_delay, max_delay + 1)
    
    return add_days(issued_at, delay_days)


# =============================================================================
# PRORATION MATH
# =============================================================================

def calculate_proration(old_price, new_price, remaining_days, total_days):
    """
    Calculate proration credit and charge for an upgrade.
    
    Args:
        old_price: Price of the old plan (per period)
        new_price: Price of the new plan (per period)
        remaining_days: Days remaining in the billing period
        total_days: Total days in the billing period
    
    Returns:
        tuple: (credit_amount, charge_amount)
        - credit is negative (refund for old plan)
        - charge is positive (cost for new plan)
    
    Example:
        # Upgrade from €30 to €60 with 20 days remaining in 30-day period
        credit, charge = calculate_proration(30, 60, 20, 30)
        # credit = -20.00, charge = +40.00
    """
    ratio = remaining_days / total_days
    credit = -old_price * ratio
    charge = new_price * ratio
    return round(credit, 2), round(charge, 2)


# =============================================================================
# FILE I/O
# =============================================================================

def save_to_csv(dataframes, output_dir):
    """
    Save DataFrames to CSV files.
    
    Args:
        dataframes: Dict of {filename: DataFrame}
        output_dir: Path to output directory
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True, parents=True)
    
    for filename, df in dataframes.items():
        filepath = output_path / filename
        df.to_csv(filepath, index=False)
        print(f"   Saved {filename} ({len(df)} rows)")