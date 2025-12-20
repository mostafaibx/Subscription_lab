"""
Deterministic edge case scenarios S001-S018.

These are EXACT test cases with known values for dbt testing.
Each scenario has specific dates, amounts, and expected outcomes.

Reference: docs/edge_cases.md

Notes:
- All datetimes are timezone-aware (UTC)
- period_end computed via calculate_period_end() helper
- paid_at included for paid invoices
- No 'renewed' events (handled by dbt logic, not source data)
"""

from utils import (
    PLANS, 
    CONFIG,
    calculate_period_end,
    utc_datetime,
    add_days
)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_plan(plan_id):
    """Get plan details by ID."""
    return PLANS[plan_id]


def compute_period_end(start_date, plan_id):
    """Compute period end date using helper."""
    plan = get_plan(plan_id)
    return calculate_period_end(start_date, plan['billing_period_months'], CONFIG)


def paid_at_from_issued(issued_at, delay_days=0):
    """Calculate paid_at as issued_at + delay."""
    return add_days(issued_at, delay_days)


# =============================================================================
# TEST CUSTOMERS (for edge case subscriptions)
# =============================================================================

def get_test_customers():
    """Generate test customers for edge case scenarios."""
    return [
        {
            'customer_id': 'CUST_TEST_001',
            'customer_name': 'Test Company S001-S006',
            'customer_segment': 'SMB',
            'country': 'DE',
            'created_at': utc_datetime(2024, 1, 1),
            'is_test_account': True
        },
        {
            'customer_id': 'CUST_TEST_002',
            'customer_name': 'Test Company S007-S012',
            'customer_segment': 'Mid-Market',
            'country': 'NL',
            'created_at': utc_datetime(2024, 1, 1),
            'is_test_account': True
        },
        {
            'customer_id': 'CUST_TEST_003',
            'customer_name': 'Test Company S013-S018',
            'customer_segment': 'Enterprise',
            'country': 'FR',
            'created_at': utc_datetime(2024, 1, 1),
            'is_test_account': True
        }
    ]


# =============================================================================
# SCENARIO GENERATORS
# =============================================================================

def s001_monthly_happy_path():
    """
    S001: Simple monthly active subscription.
    Start: 2025-01-01, Plan: Basic Monthly (€30)
    Expected MRR: €30 for entire period
    """
    plan_id = 'P_BASIC_M_30'
    start_at = utc_datetime(2025, 1, 1)
    period_end = compute_period_end(start_at.date(), plan_id)
    
    sub = {
        'subscription_id': 'S001',
        'customer_id': 'CUST_TEST_001',
        'plan_id': plan_id,
        'status': 'active',
        'start_at': start_at,
        'canceled_at': None,
        'pause_start_at': None,
        'pause_end_at': None,
        'current_period_start': start_at.date(),
        'current_period_end': period_end,
        'auto_renew': True,
        'created_at': start_at
    }
    
    events = [
        {
            'event_id': 'EVT_S001_01',
            'occurred_at': start_at,
            'effective_date': start_at.date(),
            'subscription_id': 'S001',
            'customer_id': 'CUST_TEST_001',
            'event_type': 'created',
            'old_plan_id': None,
            'new_plan_id': plan_id,
            'reason': 'Initial subscription'
        }
    ]
    
    issued_at = start_at
    invoices = [
        {
            'invoice_id': 'INV_S001_01',
            'issued_at': issued_at,
            'paid_at': paid_at_from_issued(issued_at, delay_days=1),
            'subscription_id': 'S001',
            'customer_id': 'CUST_TEST_001',
            'status': 'paid',
            'currency': 'EUR',
            'invoice_period_start': start_at.date(),
            'invoice_period_end': period_end,
            'total_amount': 30.00
        }
    ]
    
    lines = [
        {
            'invoice_line_id': 'LINE_S001_01',
            'invoice_id': 'INV_S001_01',
            'subscription_id': 'S001',
            'customer_id': 'CUST_TEST_001',
            'plan_id': plan_id,
            'line_type': 'recurring_charge',
            'amount': 30.00,
            'service_period_start': start_at.date(),
            'service_period_end': period_end,
            'quantity': 1,
            'description': 'Basic Monthly - Recurring'
        }
    ]
    
    return sub, events, invoices, lines


def s002_annual_happy_path():
    """
    S002: Simple annual active subscription.
    Start: 2025-01-01, Plan: Basic Annual (€300)
    Expected MRR: €25 (300/12)
    """
    plan_id = 'P_BASIC_A_300'
    start_at = utc_datetime(2025, 1, 1)
    period_end = compute_period_end(start_at.date(), plan_id)
    
    sub = {
        'subscription_id': 'S002',
        'customer_id': 'CUST_TEST_001',
        'plan_id': plan_id,
        'status': 'active',
        'start_at': start_at,
        'canceled_at': None,
        'pause_start_at': None,
        'pause_end_at': None,
        'current_period_start': start_at.date(),
        'current_period_end': period_end,
        'auto_renew': True,
        'created_at': start_at
    }
    
    events = [
        {
            'event_id': 'EVT_S002_01',
            'occurred_at': start_at,
            'effective_date': start_at.date(),
            'subscription_id': 'S002',
            'customer_id': 'CUST_TEST_001',
            'event_type': 'created',
            'old_plan_id': None,
            'new_plan_id': plan_id,
            'reason': 'Initial subscription'
        }
    ]
    
    issued_at = start_at
    invoices = [
        {
            'invoice_id': 'INV_S002_01',
            'issued_at': issued_at,
            'paid_at': paid_at_from_issued(issued_at, delay_days=2),
            'subscription_id': 'S002',
            'customer_id': 'CUST_TEST_001',
            'status': 'paid',
            'currency': 'EUR',
            'invoice_period_start': start_at.date(),
            'invoice_period_end': period_end,
            'total_amount': 300.00
        }
    ]
    
    lines = [
        {
            'invoice_line_id': 'LINE_S002_01',
            'invoice_id': 'INV_S002_01',
            'subscription_id': 'S002',
            'customer_id': 'CUST_TEST_001',
            'plan_id': plan_id,
            'line_type': 'recurring_charge',
            'amount': 300.00,
            'service_period_start': start_at.date(),
            'service_period_end': period_end,
            'quantity': 1,
            'description': 'Basic Annual - Recurring'
        }
    ]
    
    return sub, events, invoices, lines


def s003_first_month_churn():
    """
    S003: First-month churn.
    Start: 2025-01-01, Cancel: 2025-01-20
    Expected MRR: €30 until 2025-01-20, then €0
    """
    plan_id = 'P_BASIC_M_30'
    start_at = utc_datetime(2025, 1, 1)
    cancel_at = utc_datetime(2025, 1, 20)
    period_end = compute_period_end(start_at.date(), plan_id)
    
    sub = {
        'subscription_id': 'S003',
        'customer_id': 'CUST_TEST_001',
        'plan_id': plan_id,
        'status': 'canceled',
        'start_at': start_at,
        'canceled_at': cancel_at,
        'pause_start_at': None,
        'pause_end_at': None,
        'current_period_start': start_at.date(),
        'current_period_end': period_end,
        'auto_renew': False,
        'created_at': start_at
    }
    
    events = [
        {
            'event_id': 'EVT_S003_01',
            'occurred_at': start_at,
            'effective_date': start_at.date(),
            'subscription_id': 'S003',
            'customer_id': 'CUST_TEST_001',
            'event_type': 'created',
            'old_plan_id': None,
            'new_plan_id': plan_id,
            'reason': 'Initial subscription'
        },
        {
            'event_id': 'EVT_S003_02',
            'occurred_at': cancel_at,
            'effective_date': cancel_at.date(),
            'subscription_id': 'S003',
            'customer_id': 'CUST_TEST_001',
            'event_type': 'canceled',
            'old_plan_id': None,
            'new_plan_id': None,
            'reason': 'Customer churn - first month'
        }
    ]
    
    issued_at = start_at
    invoices = [
        {
            'invoice_id': 'INV_S003_01',
            'issued_at': issued_at,
            'paid_at': paid_at_from_issued(issued_at, delay_days=1),
            'subscription_id': 'S003',
            'customer_id': 'CUST_TEST_001',
            'status': 'paid',
            'currency': 'EUR',
            'invoice_period_start': start_at.date(),
            'invoice_period_end': period_end,
            'total_amount': 30.00
        }
    ]
    
    lines = [
        {
            'invoice_line_id': 'LINE_S003_01',
            'invoice_id': 'INV_S003_01',
            'subscription_id': 'S003',
            'customer_id': 'CUST_TEST_001',
            'plan_id': plan_id,
            'line_type': 'recurring_charge',
            'amount': 30.00,
            'service_period_start': start_at.date(),
            'service_period_end': period_end,
            'quantity': 1,
            'description': 'Basic Monthly - Recurring'
        }
    ]
    
    return sub, events, invoices, lines


def s004_long_tenure_churn():
    """
    S004: Long-tenure churn (after multiple renewals).
    Start: 2025-01-01, Plan: Pro Monthly (€60), Cancel: 2025-09-10
    """
    plan_id = 'P_PRO_M_60'
    start_at = utc_datetime(2025, 1, 1)
    cancel_at = utc_datetime(2025, 9, 10)
    # Current period at cancel time (period 9: Aug 28 - Sep 27)
    current_period_start = add_days(start_at, 8 * 30).date()  # 8 periods later
    period_end = compute_period_end(current_period_start, plan_id)
    
    sub = {
        'subscription_id': 'S004',
        'customer_id': 'CUST_TEST_001',
        'plan_id': plan_id,
        'status': 'canceled',
        'start_at': start_at,
        'canceled_at': cancel_at,
        'pause_start_at': None,
        'pause_end_at': None,
        'current_period_start': current_period_start,
        'current_period_end': period_end,
        'auto_renew': False,
        'created_at': start_at
    }
    
    events = [
        {
            'event_id': 'EVT_S004_01',
            'occurred_at': start_at,
            'effective_date': start_at.date(),
            'subscription_id': 'S004',
            'customer_id': 'CUST_TEST_001',
            'event_type': 'created',
            'old_plan_id': None,
            'new_plan_id': plan_id,
            'reason': 'Initial subscription'
        },
        {
            'event_id': 'EVT_S004_02',
            'occurred_at': cancel_at,
            'effective_date': cancel_at.date(),
            'subscription_id': 'S004',
            'customer_id': 'CUST_TEST_001',
            'event_type': 'canceled',
            'old_plan_id': None,
            'new_plan_id': None,
            'reason': 'Customer churn - long tenure'
        }
    ]
    
    issued_at = start_at
    invoices = [
        {
            'invoice_id': 'INV_S004_01',
            'issued_at': issued_at,
            'paid_at': paid_at_from_issued(issued_at, delay_days=1),
            'subscription_id': 'S004',
            'customer_id': 'CUST_TEST_001',
            'status': 'paid',
            'currency': 'EUR',
            'invoice_period_start': start_at.date(),
            'invoice_period_end': compute_period_end(start_at.date(), plan_id),
            'total_amount': 60.00
        }
    ]
    
    lines = [
        {
            'invoice_line_id': 'LINE_S004_01',
            'invoice_id': 'INV_S004_01',
            'subscription_id': 'S004',
            'customer_id': 'CUST_TEST_001',
            'plan_id': plan_id,
            'line_type': 'recurring_charge',
            'amount': 60.00,
            'service_period_start': start_at.date(),
            'service_period_end': compute_period_end(start_at.date(), plan_id),
            'quantity': 1,
            'description': 'Pro Monthly - Recurring'
        }
    ]
    
    return sub, events, invoices, lines


def s005_monthly_upgrade_prorated():
    """
    S005: Monthly upgrade mid-cycle with proration.
    Start: 2025-01-01, Upgrade: 2025-01-11 (Basic→Pro)
    Period: 30 days, remaining: 20 days
    
    Proration:
    - Credit: -30 * (20/30) = -20.00
    - Charge: +60 * (20/30) = +40.00
    """
    old_plan_id = 'P_BASIC_M_30'
    new_plan_id = 'P_PRO_M_60'
    start_at = utc_datetime(2025, 1, 1)
    upgrade_at = utc_datetime(2025, 1, 11)
    period_end = compute_period_end(start_at.date(), old_plan_id)
    
    sub = {
        'subscription_id': 'S005',
        'customer_id': 'CUST_TEST_001',
        'plan_id': new_plan_id,  # After upgrade
        'status': 'active',
        'start_at': start_at,
        'canceled_at': None,
        'pause_start_at': None,
        'pause_end_at': None,
        'current_period_start': start_at.date(),
        'current_period_end': period_end,
        'auto_renew': True,
        'created_at': start_at
    }
    
    events = [
        {
            'event_id': 'EVT_S005_01',
            'occurred_at': start_at,
            'effective_date': start_at.date(),
            'subscription_id': 'S005',
            'customer_id': 'CUST_TEST_001',
            'event_type': 'created',
            'old_plan_id': None,
            'new_plan_id': old_plan_id,
            'reason': 'Initial subscription'
        },
        {
            'event_id': 'EVT_S005_02',
            'occurred_at': upgrade_at,
            'effective_date': upgrade_at.date(),
            'subscription_id': 'S005',
            'customer_id': 'CUST_TEST_001',
            'event_type': 'plan_changed',
            'old_plan_id': old_plan_id,
            'new_plan_id': new_plan_id,
            'reason': 'Upgrade'
        }
    ]
    
    invoices = [
        {
            'invoice_id': 'INV_S005_01',
            'issued_at': start_at,
            'paid_at': paid_at_from_issued(start_at, delay_days=1),
            'subscription_id': 'S005',
            'customer_id': 'CUST_TEST_001',
            'status': 'paid',
            'currency': 'EUR',
            'invoice_period_start': start_at.date(),
            'invoice_period_end': period_end,
            'total_amount': 30.00
        },
        {
            'invoice_id': 'INV_S005_02',
            'issued_at': upgrade_at,
            'paid_at': paid_at_from_issued(upgrade_at, delay_days=0),
            'subscription_id': 'S005',
            'customer_id': 'CUST_TEST_001',
            'status': 'paid',
            'currency': 'EUR',
            'invoice_period_start': upgrade_at.date(),
            'invoice_period_end': period_end,
            'total_amount': 20.00  # -20 + 40 = 20
        }
    ]
    
    lines = [
        {
            'invoice_line_id': 'LINE_S005_01',
            'invoice_id': 'INV_S005_01',
            'subscription_id': 'S005',
            'customer_id': 'CUST_TEST_001',
            'plan_id': old_plan_id,
            'line_type': 'recurring_charge',
            'amount': 30.00,
            'service_period_start': start_at.date(),
            'service_period_end': period_end,
            'quantity': 1,
            'description': 'Basic Monthly - Recurring'
        },
        {
            'invoice_line_id': 'LINE_S005_02',
            'invoice_id': 'INV_S005_02',
            'subscription_id': 'S005',
            'customer_id': 'CUST_TEST_001',
            'plan_id': old_plan_id,
            'line_type': 'proration_credit',
            'amount': -20.00,  # EXACT: -30 * (20/30)
            'service_period_start': upgrade_at.date(),
            'service_period_end': period_end,
            'quantity': 1,
            'description': 'Proration credit for Basic Monthly'
        },
        {
            'invoice_line_id': 'LINE_S005_03',
            'invoice_id': 'INV_S005_02',
            'subscription_id': 'S005',
            'customer_id': 'CUST_TEST_001',
            'plan_id': new_plan_id,
            'line_type': 'proration_charge',
            'amount': 40.00,  # EXACT: +60 * (20/30)
            'service_period_start': upgrade_at.date(),
            'service_period_end': period_end,
            'quantity': 1,
            'description': 'Proration charge for Pro Monthly'
        }
    ]
    
    return sub, events, invoices, lines


def s006_monthly_upgrade_near_end():
    """
    S006: Monthly upgrade near period end.
    Start: 2025-01-01, Upgrade: 2025-01-28, remaining: 3 days
    
    Proration:
    - Credit: -30 * (3/30) = -3.00
    - Charge: +60 * (3/30) = +6.00
    """
    old_plan_id = 'P_BASIC_M_30'
    new_plan_id = 'P_PRO_M_60'
    start_at = utc_datetime(2025, 1, 1)
    upgrade_at = utc_datetime(2025, 1, 28)
    period_end = compute_period_end(start_at.date(), old_plan_id)
    
    sub = {
        'subscription_id': 'S006',
        'customer_id': 'CUST_TEST_001',
        'plan_id': new_plan_id,
        'status': 'active',
        'start_at': start_at,
        'canceled_at': None,
        'pause_start_at': None,
        'pause_end_at': None,
        'current_period_start': start_at.date(),
        'current_period_end': period_end,
        'auto_renew': True,
        'created_at': start_at
    }
    
    events = [
        {
            'event_id': 'EVT_S006_01',
            'occurred_at': start_at,
            'effective_date': start_at.date(),
            'subscription_id': 'S006',
            'customer_id': 'CUST_TEST_001',
            'event_type': 'created',
            'old_plan_id': None,
            'new_plan_id': old_plan_id,
            'reason': 'Initial subscription'
        },
        {
            'event_id': 'EVT_S006_02',
            'occurred_at': upgrade_at,
            'effective_date': upgrade_at.date(),
            'subscription_id': 'S006',
            'customer_id': 'CUST_TEST_001',
            'event_type': 'plan_changed',
            'old_plan_id': old_plan_id,
            'new_plan_id': new_plan_id,
            'reason': 'Upgrade near period end'
        }
    ]
    
    invoices = [
        {
            'invoice_id': 'INV_S006_01',
            'issued_at': start_at,
            'paid_at': paid_at_from_issued(start_at, delay_days=1),
            'subscription_id': 'S006',
            'customer_id': 'CUST_TEST_001',
            'status': 'paid',
            'currency': 'EUR',
            'invoice_period_start': start_at.date(),
            'invoice_period_end': period_end,
            'total_amount': 30.00
        },
        {
            'invoice_id': 'INV_S006_02',
            'issued_at': upgrade_at,
            'paid_at': paid_at_from_issued(upgrade_at, delay_days=0),
            'subscription_id': 'S006',
            'customer_id': 'CUST_TEST_001',
            'status': 'paid',
            'currency': 'EUR',
            'invoice_period_start': upgrade_at.date(),
            'invoice_period_end': period_end,
            'total_amount': 3.00  # -3 + 6 = 3
        }
    ]
    
    lines = [
        {
            'invoice_line_id': 'LINE_S006_01',
            'invoice_id': 'INV_S006_01',
            'subscription_id': 'S006',
            'customer_id': 'CUST_TEST_001',
            'plan_id': old_plan_id,
            'line_type': 'recurring_charge',
            'amount': 30.00,
            'service_period_start': start_at.date(),
            'service_period_end': period_end,
            'quantity': 1,
            'description': 'Basic Monthly - Recurring'
        },
        {
            'invoice_line_id': 'LINE_S006_02',
            'invoice_id': 'INV_S006_02',
            'subscription_id': 'S006',
            'customer_id': 'CUST_TEST_001',
            'plan_id': old_plan_id,
            'line_type': 'proration_credit',
            'amount': -3.00,  # EXACT: -30 * (3/30)
            'service_period_start': upgrade_at.date(),
            'service_period_end': period_end,
            'quantity': 1,
            'description': 'Proration credit for Basic Monthly'
        },
        {
            'invoice_line_id': 'LINE_S006_03',
            'invoice_id': 'INV_S006_02',
            'subscription_id': 'S006',
            'customer_id': 'CUST_TEST_001',
            'plan_id': new_plan_id,
            'line_type': 'proration_charge',
            'amount': 6.00,  # EXACT: +60 * (3/30)
            'service_period_start': upgrade_at.date(),
            'service_period_end': period_end,
            'quantity': 1,
            'description': 'Proration charge for Pro Monthly'
        }
    ]
    
    return sub, events, invoices, lines


def s007_annual_upgrade_prorated():
    """
    S007: Annual upgrade mid-term with proration.
    Start: 2025-01-01, Upgrade: 2025-04-01, 
    Period: 360 days, days_used: 90, remaining: 270
    
    Proration:
    - Credit: -300 * (270/360) = -225.00
    - Charge: +600 * (270/360) = +450.00
    """
    old_plan_id = 'P_BASIC_A_300'
    new_plan_id = 'P_PRO_A_600'
    start_at = utc_datetime(2025, 1, 1)
    upgrade_at = utc_datetime(2025, 4, 1)
    period_end = compute_period_end(start_at.date(), old_plan_id)
    
    sub = {
        'subscription_id': 'S007',
        'customer_id': 'CUST_TEST_002',
        'plan_id': new_plan_id,
        'status': 'active',
        'start_at': start_at,
        'canceled_at': None,
        'pause_start_at': None,
        'pause_end_at': None,
        'current_period_start': start_at.date(),
        'current_period_end': period_end,
        'auto_renew': True,
        'created_at': start_at
    }
    
    events = [
        {
            'event_id': 'EVT_S007_01',
            'occurred_at': start_at,
            'effective_date': start_at.date(),
            'subscription_id': 'S007',
            'customer_id': 'CUST_TEST_002',
            'event_type': 'created',
            'old_plan_id': None,
            'new_plan_id': old_plan_id,
            'reason': 'Initial subscription'
        },
        {
            'event_id': 'EVT_S007_02',
            'occurred_at': upgrade_at,
            'effective_date': upgrade_at.date(),
            'subscription_id': 'S007',
            'customer_id': 'CUST_TEST_002',
            'event_type': 'plan_changed',
            'old_plan_id': old_plan_id,
            'new_plan_id': new_plan_id,
            'reason': 'Annual upgrade'
        }
    ]
    
    invoices = [
        {
            'invoice_id': 'INV_S007_01',
            'issued_at': start_at,
            'paid_at': paid_at_from_issued(start_at, delay_days=3),
            'subscription_id': 'S007',
            'customer_id': 'CUST_TEST_002',
            'status': 'paid',
            'currency': 'EUR',
            'invoice_period_start': start_at.date(),
            'invoice_period_end': period_end,
            'total_amount': 300.00
        },
        {
            'invoice_id': 'INV_S007_02',
            'issued_at': upgrade_at,
            'paid_at': paid_at_from_issued(upgrade_at, delay_days=0),
            'subscription_id': 'S007',
            'customer_id': 'CUST_TEST_002',
            'status': 'paid',
            'currency': 'EUR',
            'invoice_period_start': upgrade_at.date(),
            'invoice_period_end': period_end,
            'total_amount': 225.00  # -225 + 450 = 225
        }
    ]
    
    lines = [
        {
            'invoice_line_id': 'LINE_S007_01',
            'invoice_id': 'INV_S007_01',
            'subscription_id': 'S007',
            'customer_id': 'CUST_TEST_002',
            'plan_id': old_plan_id,
            'line_type': 'recurring_charge',
            'amount': 300.00,
            'service_period_start': start_at.date(),
            'service_period_end': period_end,
            'quantity': 1,
            'description': 'Basic Annual - Recurring'
        },
        {
            'invoice_line_id': 'LINE_S007_02',
            'invoice_id': 'INV_S007_02',
            'subscription_id': 'S007',
            'customer_id': 'CUST_TEST_002',
            'plan_id': old_plan_id,
            'line_type': 'proration_credit',
            'amount': -225.00,  # EXACT: -300 * (270/360)
            'service_period_start': upgrade_at.date(),
            'service_period_end': period_end,
            'quantity': 1,
            'description': 'Proration credit for Basic Annual'
        },
        {
            'invoice_line_id': 'LINE_S007_03',
            'invoice_id': 'INV_S007_02',
            'subscription_id': 'S007',
            'customer_id': 'CUST_TEST_002',
            'plan_id': new_plan_id,
            'line_type': 'proration_charge',
            'amount': 450.00,  # EXACT: +600 * (270/360)
            'service_period_start': upgrade_at.date(),
            'service_period_end': period_end,
            'quantity': 1,
            'description': 'Proration charge for Pro Annual'
        }
    ]
    
    return sub, events, invoices, lines


def s008_two_upgrades_one_term():
    """
    S008: Upgrade in one term (tests multiple plan_changed events don't break snapshots).
    Start: 2025-01-01, Upgrade: 2025-01-06 (Basic→Pro)
    remaining_days = 25
    """
    old_plan_id = 'P_BASIC_M_30'
    new_plan_id = 'P_PRO_M_60'
    start_at = utc_datetime(2025, 1, 1)
    upgrade_at = utc_datetime(2025, 1, 6)
    period_end = compute_period_end(start_at.date(), old_plan_id)
    
    sub = {
        'subscription_id': 'S008',
        'customer_id': 'CUST_TEST_002',
        'plan_id': new_plan_id,
        'status': 'active',
        'start_at': start_at,
        'canceled_at': None,
        'pause_start_at': None,
        'pause_end_at': None,
        'current_period_start': start_at.date(),
        'current_period_end': period_end,
        'auto_renew': True,
        'created_at': start_at
    }
    
    events = [
        {
            'event_id': 'EVT_S008_01',
            'occurred_at': start_at,
            'effective_date': start_at.date(),
            'subscription_id': 'S008',
            'customer_id': 'CUST_TEST_002',
            'event_type': 'created',
            'old_plan_id': None,
            'new_plan_id': old_plan_id,
            'reason': 'Initial subscription'
        },
        {
            'event_id': 'EVT_S008_02',
            'occurred_at': upgrade_at,
            'effective_date': upgrade_at.date(),
            'subscription_id': 'S008',
            'customer_id': 'CUST_TEST_002',
            'event_type': 'plan_changed',
            'old_plan_id': old_plan_id,
            'new_plan_id': new_plan_id,
            'reason': 'First upgrade'
        }
    ]
    
    invoices = [
        {
            'invoice_id': 'INV_S008_01',
            'issued_at': start_at,
            'paid_at': paid_at_from_issued(start_at, delay_days=1),
            'subscription_id': 'S008',
            'customer_id': 'CUST_TEST_002',
            'status': 'paid',
            'currency': 'EUR',
            'invoice_period_start': start_at.date(),
            'invoice_period_end': period_end,
            'total_amount': 30.00
        },
        {
            'invoice_id': 'INV_S008_02',
            'issued_at': upgrade_at,
            'paid_at': paid_at_from_issued(upgrade_at, delay_days=0),
            'subscription_id': 'S008',
            'customer_id': 'CUST_TEST_002',
            'status': 'paid',
            'currency': 'EUR',
            'invoice_period_start': upgrade_at.date(),
            'invoice_period_end': period_end,
            'total_amount': 25.00  # -25 + 50 = 25
        }
    ]
    
    lines = [
        {
            'invoice_line_id': 'LINE_S008_01',
            'invoice_id': 'INV_S008_01',
            'subscription_id': 'S008',
            'customer_id': 'CUST_TEST_002',
            'plan_id': old_plan_id,
            'line_type': 'recurring_charge',
            'amount': 30.00,
            'service_period_start': start_at.date(),
            'service_period_end': period_end,
            'quantity': 1,
            'description': 'Basic Monthly - Recurring'
        },
        {
            'invoice_line_id': 'LINE_S008_02',
            'invoice_id': 'INV_S008_02',
            'subscription_id': 'S008',
            'customer_id': 'CUST_TEST_002',
            'plan_id': old_plan_id,
            'line_type': 'proration_credit',
            'amount': -25.00,  # -30 * (25/30)
            'service_period_start': upgrade_at.date(),
            'service_period_end': period_end,
            'quantity': 1,
            'description': 'Proration credit for Basic Monthly'
        },
        {
            'invoice_line_id': 'LINE_S008_03',
            'invoice_id': 'INV_S008_02',
            'subscription_id': 'S008',
            'customer_id': 'CUST_TEST_002',
            'plan_id': new_plan_id,
            'line_type': 'proration_charge',
            'amount': 50.00,  # +60 * (25/30)
            'service_period_start': upgrade_at.date(),
            'service_period_end': period_end,
            'quantity': 1,
            'description': 'Proration charge for Pro Monthly'
        }
    ]
    
    return sub, events, invoices, lines


def s009_monthly_downgrade_next_renewal():
    """
    S009: Monthly downgrade effective at next renewal (no proration).
    Request: 2025-01-10, Effective: period_end (next renewal)
    """
    old_plan_id = 'P_PRO_M_60'
    new_plan_id = 'P_BASIC_M_30'
    start_at = utc_datetime(2025, 1, 1)
    request_at = utc_datetime(2025, 1, 10)
    period_end = compute_period_end(start_at.date(), old_plan_id)
    
    sub = {
        'subscription_id': 'S009',
        'customer_id': 'CUST_TEST_002',
        'plan_id': old_plan_id,  # Still on Pro until renewal
        'status': 'active',
        'start_at': start_at,
        'canceled_at': None,
        'pause_start_at': None,
        'pause_end_at': None,
        'current_period_start': start_at.date(),
        'current_period_end': period_end,
        'auto_renew': True,
        'created_at': start_at
    }
    
    events = [
        {
            'event_id': 'EVT_S009_01',
            'occurred_at': start_at,
            'effective_date': start_at.date(),
            'subscription_id': 'S009',
            'customer_id': 'CUST_TEST_002',
            'event_type': 'created',
            'old_plan_id': None,
            'new_plan_id': old_plan_id,
            'reason': 'Initial subscription'
        },
        {
            'event_id': 'EVT_S009_02',
            'occurred_at': request_at,  # Request date
            'effective_date': period_end,  # EFFECTIVE AT RENEWAL
            'subscription_id': 'S009',
            'customer_id': 'CUST_TEST_002',
            'event_type': 'plan_changed',
            'old_plan_id': old_plan_id,
            'new_plan_id': new_plan_id,
            'reason': 'Downgrade - effective next renewal'
        }
    ]
    
    # No proration invoice for downgrade!
    invoices = [
        {
            'invoice_id': 'INV_S009_01',
            'issued_at': start_at,
            'paid_at': paid_at_from_issued(start_at, delay_days=1),
            'subscription_id': 'S009',
            'customer_id': 'CUST_TEST_002',
            'status': 'paid',
            'currency': 'EUR',
            'invoice_period_start': start_at.date(),
            'invoice_period_end': period_end,
            'total_amount': 60.00
        }
    ]
    
    lines = [
        {
            'invoice_line_id': 'LINE_S009_01',
            'invoice_id': 'INV_S009_01',
            'subscription_id': 'S009',
            'customer_id': 'CUST_TEST_002',
            'plan_id': old_plan_id,
            'line_type': 'recurring_charge',
            'amount': 60.00,
            'service_period_start': start_at.date(),
            'service_period_end': period_end,
            'quantity': 1,
            'description': 'Pro Monthly - Recurring'
        }
    ]
    
    return sub, events, invoices, lines


def s010_annual_downgrade_next_renewal():
    """
    S010: Annual downgrade effective at next renewal.
    Request: 2025-06-01, Effective: period_end
    """
    old_plan_id = 'P_PRO_A_600'
    new_plan_id = 'P_BASIC_A_300'
    start_at = utc_datetime(2025, 1, 1)
    request_at = utc_datetime(2025, 6, 1)
    period_end = compute_period_end(start_at.date(), old_plan_id)
    
    sub = {
        'subscription_id': 'S010',
        'customer_id': 'CUST_TEST_002',
        'plan_id': old_plan_id,  # Still on Pro until renewal
        'status': 'active',
        'start_at': start_at,
        'canceled_at': None,
        'pause_start_at': None,
        'pause_end_at': None,
        'current_period_start': start_at.date(),
        'current_period_end': period_end,
        'auto_renew': True,
        'created_at': start_at
    }
    
    events = [
        {
            'event_id': 'EVT_S010_01',
            'occurred_at': start_at,
            'effective_date': start_at.date(),
            'subscription_id': 'S010',
            'customer_id': 'CUST_TEST_002',
            'event_type': 'created',
            'old_plan_id': None,
            'new_plan_id': old_plan_id,
            'reason': 'Initial subscription'
        },
        {
            'event_id': 'EVT_S010_02',
            'occurred_at': request_at,
            'effective_date': period_end,  # EFFECTIVE AT RENEWAL
            'subscription_id': 'S010',
            'customer_id': 'CUST_TEST_002',
            'event_type': 'plan_changed',
            'old_plan_id': old_plan_id,
            'new_plan_id': new_plan_id,
            'reason': 'Downgrade - effective next renewal'
        }
    ]
    
    invoices = [
        {
            'invoice_id': 'INV_S010_01',
            'issued_at': start_at,
            'paid_at': paid_at_from_issued(start_at, delay_days=3),
            'subscription_id': 'S010',
            'customer_id': 'CUST_TEST_002',
            'status': 'paid',
            'currency': 'EUR',
            'invoice_period_start': start_at.date(),
            'invoice_period_end': period_end,
            'total_amount': 600.00
        }
    ]
    
    lines = [
        {
            'invoice_line_id': 'LINE_S010_01',
            'invoice_id': 'INV_S010_01',
            'subscription_id': 'S010',
            'customer_id': 'CUST_TEST_002',
            'plan_id': old_plan_id,
            'line_type': 'recurring_charge',
            'amount': 600.00,
            'service_period_start': start_at.date(),
            'service_period_end': period_end,
            'quantity': 1,
            'description': 'Pro Annual - Recurring'
        }
    ]
    
    return sub, events, invoices, lines


def s011_pause_resume():
    """
    S011: Pause then resume.
    Pause: 2025-01-15 → Resume: 2025-01-29 (14 days)
    MRR = 0 during pause
    """
    plan_id = 'P_BASIC_M_30'
    start_at = utc_datetime(2025, 1, 1)
    pause_at = utc_datetime(2025, 1, 15)
    resume_at = utc_datetime(2025, 1, 29)
    period_end = compute_period_end(start_at.date(), plan_id)
    
    sub = {
        'subscription_id': 'S011',
        'customer_id': 'CUST_TEST_002',
        'plan_id': plan_id,
        'status': 'active',  # After resume
        'start_at': start_at,
        'canceled_at': None,
        'pause_start_at': None,  # Cleared after resume
        'pause_end_at': None,
        'current_period_start': start_at.date(),
        'current_period_end': period_end,
        'auto_renew': True,
        'created_at': start_at
    }
    
    events = [
        {
            'event_id': 'EVT_S011_01',
            'occurred_at': start_at,
            'effective_date': start_at.date(),
            'subscription_id': 'S011',
            'customer_id': 'CUST_TEST_002',
            'event_type': 'created',
            'old_plan_id': None,
            'new_plan_id': plan_id,
            'reason': 'Initial subscription'
        },
        {
            'event_id': 'EVT_S011_02',
            'occurred_at': pause_at,
            'effective_date': pause_at.date(),
            'subscription_id': 'S011',
            'customer_id': 'CUST_TEST_002',
            'event_type': 'paused',
            'old_plan_id': None,
            'new_plan_id': None,
            'reason': 'Customer requested pause'
        },
        {
            'event_id': 'EVT_S011_03',
            'occurred_at': resume_at,
            'effective_date': resume_at.date(),
            'subscription_id': 'S011',
            'customer_id': 'CUST_TEST_002',
            'event_type': 'resumed',
            'old_plan_id': None,
            'new_plan_id': None,
            'reason': 'Subscription resumed'
        }
    ]
    
    invoices = [
        {
            'invoice_id': 'INV_S011_01',
            'issued_at': start_at,
            'paid_at': paid_at_from_issued(start_at, delay_days=1),
            'subscription_id': 'S011',
            'customer_id': 'CUST_TEST_002',
            'status': 'paid',
            'currency': 'EUR',
            'invoice_period_start': start_at.date(),
            'invoice_period_end': period_end,
            'total_amount': 30.00
        }
    ]
    
    lines = [
        {
            'invoice_line_id': 'LINE_S011_01',
            'invoice_id': 'INV_S011_01',
            'subscription_id': 'S011',
            'customer_id': 'CUST_TEST_002',
            'plan_id': plan_id,
            'line_type': 'recurring_charge',
            'amount': 30.00,
            'service_period_start': start_at.date(),
            'service_period_end': period_end,
            'quantity': 1,
            'description': 'Basic Monthly - Recurring'
        }
    ]
    
    return sub, events, invoices, lines


def s012_pause_then_cancel():
    """
    S012: Pause then cancel while paused.
    Pause: 2025-01-10, Cancel: 2025-01-20
    MRR = 0 from pause onward
    """
    plan_id = 'P_BASIC_M_30'
    start_at = utc_datetime(2025, 1, 1)
    pause_at = utc_datetime(2025, 1, 10)
    cancel_at = utc_datetime(2025, 1, 20)
    period_end = compute_period_end(start_at.date(), plan_id)
    
    sub = {
        'subscription_id': 'S012',
        'customer_id': 'CUST_TEST_002',
        'plan_id': plan_id,
        'status': 'canceled',
        'start_at': start_at,
        'canceled_at': cancel_at,
        'pause_start_at': pause_at,
        'pause_end_at': None,  # Never resumed
        'current_period_start': start_at.date(),
        'current_period_end': period_end,
        'auto_renew': False,
        'created_at': start_at
    }
    
    events = [
        {
            'event_id': 'EVT_S012_01',
            'occurred_at': start_at,
            'effective_date': start_at.date(),
            'subscription_id': 'S012',
            'customer_id': 'CUST_TEST_002',
            'event_type': 'created',
            'old_plan_id': None,
            'new_plan_id': plan_id,
            'reason': 'Initial subscription'
        },
        {
            'event_id': 'EVT_S012_02',
            'occurred_at': pause_at,
            'effective_date': pause_at.date(),
            'subscription_id': 'S012',
            'customer_id': 'CUST_TEST_002',
            'event_type': 'paused',
            'old_plan_id': None,
            'new_plan_id': None,
            'reason': 'Customer requested pause'
        },
        {
            'event_id': 'EVT_S012_03',
            'occurred_at': cancel_at,
            'effective_date': cancel_at.date(),
            'subscription_id': 'S012',
            'customer_id': 'CUST_TEST_002',
            'event_type': 'canceled',
            'old_plan_id': None,
            'new_plan_id': None,
            'reason': 'Canceled while paused'
        }
    ]
    
    invoices = [
        {
            'invoice_id': 'INV_S012_01',
            'issued_at': start_at,
            'paid_at': paid_at_from_issued(start_at, delay_days=1),
            'subscription_id': 'S012',
            'customer_id': 'CUST_TEST_002',
            'status': 'paid',
            'currency': 'EUR',
            'invoice_period_start': start_at.date(),
            'invoice_period_end': period_end,
            'total_amount': 30.00
        }
    ]
    
    lines = [
        {
            'invoice_line_id': 'LINE_S012_01',
            'invoice_id': 'INV_S012_01',
            'subscription_id': 'S012',
            'customer_id': 'CUST_TEST_002',
            'plan_id': plan_id,
            'line_type': 'recurring_charge',
            'amount': 30.00,
            'service_period_start': start_at.date(),
            'service_period_end': period_end,
            'quantity': 1,
            'description': 'Basic Monthly - Recurring'
        }
    ]
    
    return sub, events, invoices, lines


def s013_cancel_reactivate():
    """
    S013: Cancel then reactivate.
    Cancel: 2025-02-10, Reactivate: 2025-03-01
    MRR = 0 between cancel and reactivation
    """
    plan_id = 'P_BASIC_M_30'
    start_at = utc_datetime(2025, 1, 1)
    cancel_at = utc_datetime(2025, 2, 10)
    reactivate_at = utc_datetime(2025, 3, 1)
    # After reactivation, new period starts
    new_period_end = compute_period_end(reactivate_at.date(), plan_id)
    
    sub = {
        'subscription_id': 'S013',
        'customer_id': 'CUST_TEST_003',
        'plan_id': plan_id,
        'status': 'active',  # After reactivation
        'start_at': start_at,
        'canceled_at': None,  # Cleared after reactivation
        'pause_start_at': None,
        'pause_end_at': None,
        'current_period_start': reactivate_at.date(),
        'current_period_end': new_period_end,
        'auto_renew': True,
        'created_at': start_at
    }
    
    events = [
        {
            'event_id': 'EVT_S013_01',
            'occurred_at': start_at,
            'effective_date': start_at.date(),
            'subscription_id': 'S013',
            'customer_id': 'CUST_TEST_003',
            'event_type': 'created',
            'old_plan_id': None,
            'new_plan_id': plan_id,
            'reason': 'Initial subscription'
        },
        {
            'event_id': 'EVT_S013_02',
            'occurred_at': cancel_at,
            'effective_date': cancel_at.date(),
            'subscription_id': 'S013',
            'customer_id': 'CUST_TEST_003',
            'event_type': 'canceled',
            'old_plan_id': None,
            'new_plan_id': None,
            'reason': 'Customer churn'
        },
        {
            'event_id': 'EVT_S013_03',
            'occurred_at': reactivate_at,
            'effective_date': reactivate_at.date(),
            'subscription_id': 'S013',
            'customer_id': 'CUST_TEST_003',
            'event_type': 'reactivated',
            'old_plan_id': None,
            'new_plan_id': plan_id,
            'reason': 'Customer returned'
        }
    ]
    
    first_period_end = compute_period_end(start_at.date(), plan_id)
    invoices = [
        {
            'invoice_id': 'INV_S013_01',
            'issued_at': start_at,
            'paid_at': paid_at_from_issued(start_at, delay_days=1),
            'subscription_id': 'S013',
            'customer_id': 'CUST_TEST_003',
            'status': 'paid',
            'currency': 'EUR',
            'invoice_period_start': start_at.date(),
            'invoice_period_end': first_period_end,
            'total_amount': 30.00
        },
        {
            'invoice_id': 'INV_S013_02',
            'issued_at': reactivate_at,
            'paid_at': paid_at_from_issued(reactivate_at, delay_days=0),
            'subscription_id': 'S013',
            'customer_id': 'CUST_TEST_003',
            'status': 'paid',
            'currency': 'EUR',
            'invoice_period_start': reactivate_at.date(),
            'invoice_period_end': new_period_end,
            'total_amount': 30.00
        }
    ]
    
    lines = [
        {
            'invoice_line_id': 'LINE_S013_01',
            'invoice_id': 'INV_S013_01',
            'subscription_id': 'S013',
            'customer_id': 'CUST_TEST_003',
            'plan_id': plan_id,
            'line_type': 'recurring_charge',
            'amount': 30.00,
            'service_period_start': start_at.date(),
            'service_period_end': first_period_end,
            'quantity': 1,
            'description': 'Basic Monthly - Recurring'
        },
        {
            'invoice_line_id': 'LINE_S013_02',
            'invoice_id': 'INV_S013_02',
            'subscription_id': 'S013',
            'customer_id': 'CUST_TEST_003',
            'plan_id': plan_id,
            'line_type': 'recurring_charge',
            'amount': 30.00,
            'service_period_start': reactivate_at.date(),
            'service_period_end': new_period_end,
            'quantity': 1,
            'description': 'Basic Monthly - Recurring (reactivation)'
        }
    ]
    
    return sub, events, invoices, lines


def s014_payment_failed_recovered():
    """
    S014: Payment failed → delinquent → recovered.
    Failed: 2025-01-31, Recovered: 2025-02-10
    MRR = 0 during delinquent window
    """
    plan_id = 'P_BASIC_M_30'
    start_at = utc_datetime(2025, 1, 1)
    failed_at = utc_datetime(2025, 1, 31)
    recovered_at = utc_datetime(2025, 2, 10)
    first_period_end = compute_period_end(start_at.date(), plan_id)
    second_period_end = compute_period_end(first_period_end, plan_id)
    
    sub = {
        'subscription_id': 'S014',
        'customer_id': 'CUST_TEST_003',
        'plan_id': plan_id,
        'status': 'active',  # After recovery
        'start_at': start_at,
        'canceled_at': None,
        'pause_start_at': None,
        'pause_end_at': None,
        'current_period_start': first_period_end,
        'current_period_end': second_period_end,
        'auto_renew': True,
        'created_at': start_at
    }
    
    events = [
        {
            'event_id': 'EVT_S014_01',
            'occurred_at': start_at,
            'effective_date': start_at.date(),
            'subscription_id': 'S014',
            'customer_id': 'CUST_TEST_003',
            'event_type': 'created',
            'old_plan_id': None,
            'new_plan_id': plan_id,
            'reason': 'Initial subscription'
        },
        {
            'event_id': 'EVT_S014_02',
            'occurred_at': failed_at,
            'effective_date': failed_at.date(),
            'subscription_id': 'S014',
            'customer_id': 'CUST_TEST_003',
            'event_type': 'payment_failed',
            'old_plan_id': None,
            'new_plan_id': None,
            'reason': 'Payment method declined'
        },
        {
            'event_id': 'EVT_S014_03',
            'occurred_at': recovered_at,
            'effective_date': recovered_at.date(),
            'subscription_id': 'S014',
            'customer_id': 'CUST_TEST_003',
            'event_type': 'payment_recovered',
            'old_plan_id': None,
            'new_plan_id': None,
            'reason': 'Payment recovered'
        }
    ]
    
    invoices = [
        {
            'invoice_id': 'INV_S014_01',
            'issued_at': start_at,
            'paid_at': paid_at_from_issued(start_at, delay_days=1),
            'subscription_id': 'S014',
            'customer_id': 'CUST_TEST_003',
            'status': 'paid',
            'currency': 'EUR',
            'invoice_period_start': start_at.date(),
            'invoice_period_end': first_period_end,
            'total_amount': 30.00
        },
        {
            'invoice_id': 'INV_S014_02',
            'issued_at': failed_at,
            'paid_at': None,  # Never paid - uncollectible
            'subscription_id': 'S014',
            'customer_id': 'CUST_TEST_003',
            'status': 'uncollectible',  # Failed payment
            'currency': 'EUR',
            'invoice_period_start': first_period_end,
            'invoice_period_end': second_period_end,
            'total_amount': 30.00
        }
    ]
    
    lines = [
        {
            'invoice_line_id': 'LINE_S014_01',
            'invoice_id': 'INV_S014_01',
            'subscription_id': 'S014',
            'customer_id': 'CUST_TEST_003',
            'plan_id': plan_id,
            'line_type': 'recurring_charge',
            'amount': 30.00,
            'service_period_start': start_at.date(),
            'service_period_end': first_period_end,
            'quantity': 1,
            'description': 'Basic Monthly - Recurring'
        },
        {
            'invoice_line_id': 'LINE_S014_02',
            'invoice_id': 'INV_S014_02',
            'subscription_id': 'S014',
            'customer_id': 'CUST_TEST_003',
            'plan_id': plan_id,
            'line_type': 'recurring_charge',
            'amount': 30.00,
            'service_period_start': first_period_end,
            'service_period_end': second_period_end,
            'quantity': 1,
            'description': 'Basic Monthly - Recurring (failed)'
        }
    ]
    
    return sub, events, invoices, lines


def s015_missing_invoice():
    """
    S015: Missing invoice for an active period.
    Active subscription but no invoice for Feb period.
    Contract MRR continues, billing audit shows gap.
    """
    plan_id = 'P_BASIC_M_30'
    start_at = utc_datetime(2025, 1, 1)
    first_period_end = compute_period_end(start_at.date(), plan_id)
    second_period_end = compute_period_end(first_period_end, plan_id)
    
    sub = {
        'subscription_id': 'S015',
        'customer_id': 'CUST_TEST_003',
        'plan_id': plan_id,
        'status': 'active',
        'start_at': start_at,
        'canceled_at': None,
        'pause_start_at': None,
        'pause_end_at': None,
        'current_period_start': first_period_end,
        'current_period_end': second_period_end,
        'auto_renew': True,
        'created_at': start_at
    }
    
    events = [
        {
            'event_id': 'EVT_S015_01',
            'occurred_at': start_at,
            'effective_date': start_at.date(),
            'subscription_id': 'S015',
            'customer_id': 'CUST_TEST_003',
            'event_type': 'created',
            'old_plan_id': None,
            'new_plan_id': plan_id,
            'reason': 'Initial subscription'
        }
    ]
    
    # Only January invoice - February is MISSING
    invoices = [
        {
            'invoice_id': 'INV_S015_01',
            'issued_at': start_at,
            'paid_at': paid_at_from_issued(start_at, delay_days=1),
            'subscription_id': 'S015',
            'customer_id': 'CUST_TEST_003',
            'status': 'paid',
            'currency': 'EUR',
            'invoice_period_start': start_at.date(),
            'invoice_period_end': first_period_end,
            'total_amount': 30.00
        }
        # NO invoice for second period - intentional gap
    ]
    
    lines = [
        {
            'invoice_line_id': 'LINE_S015_01',
            'invoice_id': 'INV_S015_01',
            'subscription_id': 'S015',
            'customer_id': 'CUST_TEST_003',
            'plan_id': plan_id,
            'line_type': 'recurring_charge',
            'amount': 30.00,
            'service_period_start': start_at.date(),
            'service_period_end': first_period_end,
            'quantity': 1,
            'description': 'Basic Monthly - Recurring'
        }
    ]
    
    return sub, events, invoices, lines


def s016_adjustment_line():
    """
    S016: Adjustment line (billing correction).
    Regular invoice with a -5.00 adjustment.
    Contract MRR unaffected.
    """
    plan_id = 'P_BASIC_M_30'
    start_at = utc_datetime(2025, 1, 1)
    period_end = compute_period_end(start_at.date(), plan_id)
    
    sub = {
        'subscription_id': 'S016',
        'customer_id': 'CUST_TEST_003',
        'plan_id': plan_id,
        'status': 'active',
        'start_at': start_at,
        'canceled_at': None,
        'pause_start_at': None,
        'pause_end_at': None,
        'current_period_start': start_at.date(),
        'current_period_end': period_end,
        'auto_renew': True,
        'created_at': start_at
    }
    
    events = [
        {
            'event_id': 'EVT_S016_01',
            'occurred_at': start_at,
            'effective_date': start_at.date(),
            'subscription_id': 'S016',
            'customer_id': 'CUST_TEST_003',
            'event_type': 'created',
            'old_plan_id': None,
            'new_plan_id': plan_id,
            'reason': 'Initial subscription'
        }
    ]
    
    invoices = [
        {
            'invoice_id': 'INV_S016_01',
            'issued_at': start_at,
            'paid_at': paid_at_from_issued(start_at, delay_days=1),
            'subscription_id': 'S016',
            'customer_id': 'CUST_TEST_003',
            'status': 'paid',
            'currency': 'EUR',
            'invoice_period_start': start_at.date(),
            'invoice_period_end': period_end,
            'total_amount': 25.00  # 30 - 5 adjustment
        }
    ]
    
    lines = [
        {
            'invoice_line_id': 'LINE_S016_01',
            'invoice_id': 'INV_S016_01',
            'subscription_id': 'S016',
            'customer_id': 'CUST_TEST_003',
            'plan_id': plan_id,
            'line_type': 'recurring_charge',
            'amount': 30.00,
            'service_period_start': start_at.date(),
            'service_period_end': period_end,
            'quantity': 1,
            'description': 'Basic Monthly - Recurring'
        },
        {
            'invoice_line_id': 'LINE_S016_02',
            'invoice_id': 'INV_S016_01',
            'subscription_id': 'S016',
            'customer_id': 'CUST_TEST_003',
            'plan_id': plan_id,
            'line_type': 'adjustment',
            'amount': -5.00,  # EXACT adjustment
            'service_period_start': start_at.date(),
            'service_period_end': period_end,
            'quantity': 1,
            'description': 'Billing adjustment - goodwill credit'
        }
    ]
    
    return sub, events, invoices, lines


def s017_starts_at_boundary():
    """
    S017: Subscription starts at month boundary.
    Start: 2025-01-31 (date spine stress test)
    """
    plan_id = 'P_BASIC_M_30'
    start_at = utc_datetime(2025, 1, 31)
    period_end = compute_period_end(start_at.date(), plan_id)
    
    sub = {
        'subscription_id': 'S017',
        'customer_id': 'CUST_TEST_003',
        'plan_id': plan_id,
        'status': 'active',
        'start_at': start_at,
        'canceled_at': None,
        'pause_start_at': None,
        'pause_end_at': None,
        'current_period_start': start_at.date(),
        'current_period_end': period_end,
        'auto_renew': True,
        'created_at': start_at
    }
    
    events = [
        {
            'event_id': 'EVT_S017_01',
            'occurred_at': start_at,
            'effective_date': start_at.date(),
            'subscription_id': 'S017',
            'customer_id': 'CUST_TEST_003',
            'event_type': 'created',
            'old_plan_id': None,
            'new_plan_id': plan_id,
            'reason': 'Initial subscription'
        }
    ]
    
    invoices = [
        {
            'invoice_id': 'INV_S017_01',
            'issued_at': start_at,
            'paid_at': paid_at_from_issued(start_at, delay_days=1),
            'subscription_id': 'S017',
            'customer_id': 'CUST_TEST_003',
            'status': 'paid',
            'currency': 'EUR',
            'invoice_period_start': start_at.date(),
            'invoice_period_end': period_end,
            'total_amount': 30.00
        }
    ]
    
    lines = [
        {
            'invoice_line_id': 'LINE_S017_01',
            'invoice_id': 'INV_S017_01',
            'subscription_id': 'S017',
            'customer_id': 'CUST_TEST_003',
            'plan_id': plan_id,
            'line_type': 'recurring_charge',
            'amount': 30.00,
            'service_period_start': start_at.date(),
            'service_period_end': period_end,
            'quantity': 1,
            'description': 'Basic Monthly - Recurring'
        }
    ]
    
    return sub, events, invoices, lines


def s018_annual_mid_start_upgrade():
    """
    S018: Annual starts mid-term + upgrade later.
    Start: 2025-02-10, Upgrade: 2025-06-10
    remaining_days = 240
    
    Proration:
    - Credit: -300 * (240/360) = -200.00
    - Charge: +600 * (240/360) = +400.00
    """
    old_plan_id = 'P_BASIC_A_300'
    new_plan_id = 'P_PRO_A_600'
    start_at = utc_datetime(2025, 2, 10)
    upgrade_at = utc_datetime(2025, 6, 10)
    period_end = compute_period_end(start_at.date(), old_plan_id)
    
    sub = {
        'subscription_id': 'S018',
        'customer_id': 'CUST_TEST_003',
        'plan_id': new_plan_id,
        'status': 'active',
        'start_at': start_at,
        'canceled_at': None,
        'pause_start_at': None,
        'pause_end_at': None,
        'current_period_start': start_at.date(),
        'current_period_end': period_end,
        'auto_renew': True,
        'created_at': start_at
    }
    
    events = [
        {
            'event_id': 'EVT_S018_01',
            'occurred_at': start_at,
            'effective_date': start_at.date(),
            'subscription_id': 'S018',
            'customer_id': 'CUST_TEST_003',
            'event_type': 'created',
            'old_plan_id': None,
            'new_plan_id': old_plan_id,
            'reason': 'Initial subscription'
        },
        {
            'event_id': 'EVT_S018_02',
            'occurred_at': upgrade_at,
            'effective_date': upgrade_at.date(),
            'subscription_id': 'S018',
            'customer_id': 'CUST_TEST_003',
            'event_type': 'plan_changed',
            'old_plan_id': old_plan_id,
            'new_plan_id': new_plan_id,
            'reason': 'Annual upgrade mid-term'
        }
    ]
    
    invoices = [
        {
            'invoice_id': 'INV_S018_01',
            'issued_at': start_at,
            'paid_at': paid_at_from_issued(start_at, delay_days=3),
            'subscription_id': 'S018',
            'customer_id': 'CUST_TEST_003',
            'status': 'paid',
            'currency': 'EUR',
            'invoice_period_start': start_at.date(),
            'invoice_period_end': period_end,
            'total_amount': 300.00
        },
        {
            'invoice_id': 'INV_S018_02',
            'issued_at': upgrade_at,
            'paid_at': paid_at_from_issued(upgrade_at, delay_days=0),
            'subscription_id': 'S018',
            'customer_id': 'CUST_TEST_003',
            'status': 'paid',
            'currency': 'EUR',
            'invoice_period_start': upgrade_at.date(),
            'invoice_period_end': period_end,
            'total_amount': 200.00  # -200 + 400 = 200
        }
    ]
    
    lines = [
        {
            'invoice_line_id': 'LINE_S018_01',
            'invoice_id': 'INV_S018_01',
            'subscription_id': 'S018',
            'customer_id': 'CUST_TEST_003',
            'plan_id': old_plan_id,
            'line_type': 'recurring_charge',
            'amount': 300.00,
            'service_period_start': start_at.date(),
            'service_period_end': period_end,
            'quantity': 1,
            'description': 'Basic Annual - Recurring'
        },
        {
            'invoice_line_id': 'LINE_S018_02',
            'invoice_id': 'INV_S018_02',
            'subscription_id': 'S018',
            'customer_id': 'CUST_TEST_003',
            'plan_id': old_plan_id,
            'line_type': 'proration_credit',
            'amount': -200.00,  # EXACT: -300 * (240/360)
            'service_period_start': upgrade_at.date(),
            'service_period_end': period_end,
            'quantity': 1,
            'description': 'Proration credit for Basic Annual'
        },
        {
            'invoice_line_id': 'LINE_S018_03',
            'invoice_id': 'INV_S018_02',
            'subscription_id': 'S018',
            'customer_id': 'CUST_TEST_003',
            'plan_id': new_plan_id,
            'line_type': 'proration_charge',
            'amount': 400.00,  # EXACT: +600 * (240/360)
            'service_period_start': upgrade_at.date(),
            'service_period_end': period_end,
            'quantity': 1,
            'description': 'Proration charge for Pro Annual'
        }
    ]
    
    return sub, events, invoices, lines


# =============================================================================
# MAIN GENERATOR
# =============================================================================

def generate_all_edge_cases():
    """
    Generate all deterministic edge case data.
    Returns: (customers, subscriptions, events, invoices, invoice_lines)
    """
    customers = get_test_customers()
    
    # Collect all scenario generators
    scenarios = [
        s001_monthly_happy_path,
        s002_annual_happy_path,
        s003_first_month_churn,
        s004_long_tenure_churn,
        s005_monthly_upgrade_prorated,
        s006_monthly_upgrade_near_end,
        s007_annual_upgrade_prorated,
        s008_two_upgrades_one_term,
        s009_monthly_downgrade_next_renewal,
        s010_annual_downgrade_next_renewal,
        s011_pause_resume,
        s012_pause_then_cancel,
        s013_cancel_reactivate,
        s014_payment_failed_recovered,
        s015_missing_invoice,
        s016_adjustment_line,
        s017_starts_at_boundary,
        s018_annual_mid_start_upgrade,
    ]
    
    all_subs = []
    all_events = []
    all_invoices = []
    all_lines = []
    
    for scenario_fn in scenarios:
        sub, events, invoices, lines = scenario_fn()
        all_subs.append(sub)
        all_events.extend(events)
        all_invoices.extend(invoices)
        all_lines.extend(lines)
    
    return customers, all_subs, all_events, all_invoices, all_lines


if __name__ == '__main__':
    # Quick test
    customers, subs, events, invoices, lines = generate_all_edge_cases()
    print(f"Generated {len(customers)} test customers")
    print(f"Generated {len(subs)} subscriptions (S001-S018)")
    print(f"Generated {len(events)} events")
    print(f"Generated {len(invoices)} invoices")
    print(f"Generated {len(lines)} invoice lines")
    
    # Verify timezone-aware
    sample_dt = subs[0]['start_at']
    print(f"\nTimezone check: {sample_dt} (tzinfo={sample_dt.tzinfo})")
    
    # Verify period_end computed
    print(f"S001 period_end: {subs[0]['current_period_end']}")
    print(f"S002 period_end: {subs[1]['current_period_end']} (annual)")
