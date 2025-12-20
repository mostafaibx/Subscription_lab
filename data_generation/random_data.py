"""
Random data generator for bulk subscription data.

Generates realistic random subscriptions with various lifecycle events.
Uses probabilities from config.yml to determine edge case frequency.

Notes:
- All datetimes are timezone-aware (UTC)
- period_end computed via calculate_period_end() helper
- paid_at included for paid invoices
"""

from datetime import datetime
import numpy as np
from faker import Faker

from utils import (
    generate_id,
    add_days,
    get_term_days,
    calculate_proration,
    calculate_period_end,
    to_utc,
    PLANS,
)


def create_event(counter, occurred_at, subscription_id, customer_id, 
                 event_type, old_plan_id=None, new_plan_id=None, reason=None):
    """
    Create a subscription event dictionary.
    
    Args:
        counter: Event counter for ID generation
        occurred_at: When the event occurred (datetime)
        subscription_id: Associated subscription
        customer_id: Associated customer
        event_type: Type of event (created, canceled, paused, etc.)
        old_plan_id: Previous plan (for plan changes)
        new_plan_id: New plan (for plan changes)
        reason: Human-readable reason
    
    Returns:
        Event dictionary
    """
    return {
        'event_id': generate_id('EVT', counter, width=6),
        'occurred_at': occurred_at,
        'effective_date': occurred_at.date(),
        'subscription_id': subscription_id,
        'customer_id': customer_id,
        'event_type': event_type,
        'old_plan_id': old_plan_id,
        'new_plan_id': new_plan_id,
        'reason': reason
    }



def generate_random_customers(config, start_id=1):
    """
    Generate random customer records.
    
    Args:
        config: Configuration dictionary
        start_id: Starting ID number (to avoid conflicts with edge cases)
    
    Returns:
        List of customer dictionaries
    """
    fake = Faker()
    customers = []
    
    start_date = to_utc(datetime.fromisoformat(config['date_range']['start_date']))
    
    for i in range(start_id, start_id + config['sizes']['random_customers']):
        # Generate created_at in the past (1-2 years before start_date)
        days_ago = np.random.randint(365, 730)
        created_at = add_days(start_date, -days_ago)
        
        customers.append({
            'customer_id': generate_id('CUST', i),
            'customer_name': fake.company(),
            'customer_segment': np.random.choice(config['randomization']['segments']),
            'country': np.random.choice(config['randomization']['countries']),
            'created_at': created_at,
            'is_test_account': False
        })
    
    return customers


def generate_random_subscriptions(customers, config, start_id=1):
    """
    Generate random subscriptions with lifecycle events, invoices, and lines.
    
    Args:
        customers: List of customer records
        config: Configuration dictionary
        start_id: Starting ID for subscriptions
    
    Returns:
        Tuple of (subscriptions, events, invoices, invoice_lines)
    """
    subscriptions = []
    events = []
    invoices = []
    invoice_lines = []
    
    event_counter = 1
    invoice_counter = 1
    line_counter = 1
    
    # Parse date range
    start_date = to_utc(datetime.fromisoformat(config['date_range']['start_date']))
    end_date = to_utc(datetime.fromisoformat(config['date_range']['end_date']))
    days_range = (end_date - start_date).days
    
    # Get plan list
    plan_list = list(PLANS.values())
    customer_ids = [c['customer_id'] for c in customers]
    
    for i in range(start_id, start_id + config['sizes']['random_subscriptions']):
        subscription_id = generate_id('SUB', i)
        customer_id = np.random.choice(customer_ids)
        
        # Random start date
        start_offset = np.random.randint(0, max(1, days_range - 60))
        sub_start = add_days(start_date, start_offset)
        
        # Pick initial plan
        initial_plan = np.random.choice(plan_list)
        current_plan_id = initial_plan['plan_id']
        term_days = get_term_days(initial_plan['billing_period_months'], config)
        
        # Compute period end using helper
        current_period_start = sub_start.date()
        current_period_end = calculate_period_end(
            current_period_start, 
            initial_plan['billing_period_months'], 
            config
        )
        
        # Initialize state
        status = 'active'
        canceled_at = None
        pause_start_at = None
        pause_end_at = None
        auto_renew = True
        
        # Track what events we've applied (to avoid conflicts)
        has_canceled = False
        upgrade_date = None
        
        # --- CREATED EVENT ---
        events.append(create_event(
            event_counter, sub_start, subscription_id, customer_id,
            'created', new_plan_id=current_plan_id, reason='Initial subscription'
        ))
        event_counter += 1
        
        # --- INITIAL INVOICE ---
        skip_invoice = np.random.random() < config['randomization']['prob_missing_invoice']
        
        if not skip_invoice:
            invoice_id = generate_id('INV', invoice_counter, width=6)
            invoice_counter += 1
            
            # Determine invoice status and paid_at
            is_uncollectible = np.random.random() < config['invoices']['prob_uncollectible']
            invoice_status = 'uncollectible' if is_uncollectible else 'paid'
            
            # Calculate paid_at for paid invoices
            if invoice_status == 'paid':
                pay_delay = np.random.randint(
                    config['invoices']['pay_delay_days_min'],
                    config['invoices']['pay_delay_days_max'] + 1
                )
                paid_at = add_days(sub_start, pay_delay)
            else:
                paid_at = None
            
            invoices.append({
                'invoice_id': invoice_id,
                'issued_at': sub_start,
                'paid_at': paid_at,
                'subscription_id': subscription_id,
                'customer_id': customer_id,
                'status': invoice_status,
                'currency': config['currency'],
                'invoice_period_start': current_period_start,
                'invoice_period_end': current_period_end,
                'total_amount': initial_plan['price_per_period']
            })
            
            invoice_lines.append({
                'invoice_line_id': generate_id('LINE', line_counter, width=8),
                'invoice_id': invoice_id,
                'subscription_id': subscription_id,
                'customer_id': customer_id,
                'plan_id': current_plan_id,
                'line_type': 'recurring_charge',
                'amount': initial_plan['price_per_period'],
                'service_period_start': current_period_start,
                'service_period_end': current_period_end,
                'quantity': 1,
                'description': f"{initial_plan['plan_name']} - Recurring"
            })
            line_counter += 1
            
            # --- ADJUSTMENT LINE ---
            if np.random.random() < config['randomization']['prob_adjustment_line']:
                adjustment = np.random.choice(config['randomization']['adjustment_amounts'])
                invoice_lines.append({
                    'invoice_line_id': generate_id('LINE', line_counter, width=8),
                    'invoice_id': invoice_id,
                    'subscription_id': subscription_id,
                    'customer_id': customer_id,
                    'plan_id': current_plan_id,
                    'line_type': 'adjustment',
                    'amount': adjustment,
                    'service_period_start': current_period_start,
                    'service_period_end': current_period_end,
                    'quantity': 1,
                    'description': 'Billing adjustment'
                })
                line_counter += 1
                # Update invoice total
                invoices[-1]['total_amount'] += adjustment
        
        # --- UPGRADE (proration) ---
        if np.random.random() < config['randomization']['prob_upgrade']:
            # Find higher-tier plan with same billing period
            same_period_plans = [p for p in plan_list 
                                 if p['billing_period_months'] == initial_plan['billing_period_months']
                                 and p['price_per_period'] > initial_plan['price_per_period']]
            
            if same_period_plans:
                new_plan = np.random.choice(same_period_plans)
                upgrade_min = config['randomization']['upgrade_days_min']
                days_into_term = np.random.randint(upgrade_min, max(upgrade_min + 1, term_days - upgrade_min))
                upgrade_date = add_days(current_period_start, days_into_term)
                
                events.append(create_event(
                    event_counter, upgrade_date, subscription_id, customer_id,
                    'plan_changed', old_plan_id=current_plan_id, 
                    new_plan_id=new_plan['plan_id'], reason='Upgrade'
                ))
                event_counter += 1
                
                # Calculate proration
                remaining_days = term_days - days_into_term
                credit, charge = calculate_proration(
                    initial_plan['price_per_period'],
                    new_plan['price_per_period'],
                    remaining_days,
                    term_days
                )
                
                # Proration invoice
                proration_invoice_id = generate_id('INV', invoice_counter, width=6)
                invoice_counter += 1
                
                invoices.append({
                    'invoice_id': proration_invoice_id,
                    'issued_at': upgrade_date,
                    'paid_at': upgrade_date,  # Paid immediately
                    'subscription_id': subscription_id,
                    'customer_id': customer_id,
                    'status': 'paid',
                    'currency': config['currency'],
                    'invoice_period_start': upgrade_date.date(),
                    'invoice_period_end': current_period_end,
                    'total_amount': round(credit + charge, 2)
                })
                
                # Credit line
                invoice_lines.append({
                    'invoice_line_id': generate_id('LINE', line_counter, width=8),
                    'invoice_id': proration_invoice_id,
                    'subscription_id': subscription_id,
                    'customer_id': customer_id,
                    'plan_id': current_plan_id,
                    'line_type': 'proration_credit',
                    'amount': credit,
                    'service_period_start': upgrade_date.date(),
                    'service_period_end': current_period_end,
                    'quantity': 1,
                    'description': f"Proration credit for {initial_plan['plan_name']}"
                })
                line_counter += 1
                
                # Charge line
                invoice_lines.append({
                    'invoice_line_id': generate_id('LINE', line_counter, width=8),
                    'invoice_id': proration_invoice_id,
                    'subscription_id': subscription_id,
                    'customer_id': customer_id,
                    'plan_id': new_plan['plan_id'],
                    'line_type': 'proration_charge',
                    'amount': charge,
                    'service_period_start': upgrade_date.date(),
                    'service_period_end': current_period_end,
                    'quantity': 1,
                    'description': f"Proration charge for {new_plan['plan_name']}"
                })
                line_counter += 1
                
                current_plan_id = new_plan['plan_id']
        
        # --- PAUSE / RESUME ---
        if np.random.random() < config['randomization']['prob_pause'] and not has_canceled:
            rand = config['randomization']
            pause_offset = np.random.randint(rand['pause_offset_min'], min(rand['pause_offset_max'], term_days - 10))
            pause_start = add_days(sub_start, pause_offset)
            pause_duration = np.random.randint(rand['pause_duration_min'], rand['pause_duration_max'])
            pause_end = add_days(pause_start, pause_duration)
            
            # Make sure pause doesn't conflict with upgrade
            if upgrade_date is None or pause_start > upgrade_date:
                has_paused = True
                
                events.append(create_event(
                    event_counter, pause_start, subscription_id, customer_id,
                    'paused', reason='Customer requested pause'
                ))
                event_counter += 1
                
                events.append(create_event(
                    event_counter, pause_end, subscription_id, customer_id,
                    'resumed', reason='Subscription resumed'
                ))
                event_counter += 1
        
        # --- CANCELLATION ---
        if np.random.random() < config['randomization']['prob_cancel']:
            rand = config['randomization']
            cancel_offset = np.random.randint(rand['cancel_days_min'], rand['cancel_days_max'])
            cancel_date = add_days(sub_start, cancel_offset)
            
            has_canceled = True
            status = 'canceled'
            canceled_at = cancel_date
            auto_renew = False
            
            events.append(create_event(
                event_counter, cancel_date, subscription_id, customer_id,
                'canceled', reason='Customer churn'
            ))
            event_counter += 1
        
        # --- DELINQUENCY (payment failure → recovery) ---
        if np.random.random() < config['randomization']['prob_delinquent'] and not has_canceled:
            rand = config['randomization']
            failed_offset = np.random.randint(rand['delinquent_offset_min'], rand['delinquent_offset_max'])
            failed_date = add_days(sub_start, failed_offset)
            recovery_days = np.random.randint(rand['recovery_days_min'], rand['recovery_days_max'])
            recovered_date = add_days(failed_date, recovery_days)
            
            events.append(create_event(
                event_counter, failed_date, subscription_id, customer_id,
                'payment_failed', reason='Payment method failed'
            ))
            event_counter += 1
            
            events.append(create_event(
                event_counter, recovered_date, subscription_id, customer_id,
                'payment_recovered', reason='Payment recovered'
            ))
            event_counter += 1
        
        # --- BUILD SUBSCRIPTION RECORD ---
        subscriptions.append({
            'subscription_id': subscription_id,
            'customer_id': customer_id,
            'plan_id': current_plan_id,
            'status': status,
            'start_at': sub_start,
            'canceled_at': canceled_at,
            'pause_start_at': pause_start_at,
            'pause_end_at': pause_end_at,
            'current_period_start': current_period_start,
            'current_period_end': current_period_end,
            'auto_renew': auto_renew,
            'created_at': sub_start
        })
    
    return subscriptions, events, invoices, invoice_lines


def generate_all_random_data(config):
    """
    Generate all random data.
    
    Args:
        config: Configuration dictionary
    
    Returns:
        Tuple of (customers, subscriptions, events, invoices, invoice_lines)
    """
    # Start IDs after edge case test data (100+)
    customers = generate_random_customers(config, start_id=100)
    subscriptions, events, invoices, invoice_lines = generate_random_subscriptions(
        customers, config, start_id=100
    )
    
    return customers, subscriptions, events, invoices, invoice_lines


if __name__ == '__main__':
    import yaml
    
    # Quick test
    with open('config.yml', 'r') as f:
        test_config = yaml.safe_load(f)
    
    np.random.seed(test_config['seed'])
    Faker.seed(test_config['seed'])
    
    customers, subs, events, invoices, lines = generate_all_random_data(test_config)
    print(f"Generated {len(customers)} random customers")
    print(f"Generated {len(subs)} random subscriptions")
    print(f"Generated {len(events)} events")
    print(f"Generated {len(invoices)} invoices")
    print(f"Generated {len(lines)} invoice lines")
    
    # Verify timezone-aware
    if subs:
        sample_dt = subs[0]['start_at']
        print(f"\nTimezone check: {sample_dt} (tzinfo={sample_dt.tzinfo})")
    
    # Verify paid_at
    paid_invoices = [inv for inv in invoices if inv['paid_at'] is not None]
    print(f"Invoices with paid_at: {len(paid_invoices)}/{len(invoices)}")
