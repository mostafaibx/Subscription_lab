#!/usr/bin/env python3
"""
Main entry point for subscription data generation.

Generates two types of data:
1. Deterministic edge cases (S001-S018) - for dbt testing
2. Random bulk data - for volume and variety

Notes:
- All datetimes are timezone-aware (UTC)
- Invoices include paid_at field
- period_end computed via helpers (not hardcoded)

Usage:
    python3 generate.py
    python3 generate.py --edge-cases-only
    python3 generate.py --random-only
"""

import argparse
import pandas as pd
import numpy as np
from faker import Faker

from utils import CONFIG, save_to_csv
from edge_cases import generate_all_edge_cases
from random_data import generate_all_random_data


def generate_plans_df(config):
    """Generate plans DataFrame from config."""
    plans = []
    for plan in config['plans']:
        mrr = plan['price_per_period'] / plan['billing_period_months']
        plans.append({
            'plan_id': plan['plan_id'],
            'plan_name': plan['plan_name'],
            'currency': config['currency'],
            'billing_period_months': plan['billing_period_months'],
            'price_per_period': plan['price_per_period'],
            'mrr_equivalent': round(mrr, 2),
            'is_active': plan['is_active']
        })
    return pd.DataFrame(plans)


def combine_data(edge_data, random_data):
    """
    Combine edge case data with random data.
    
    Args:
        edge_data: Tuple of (customers, subs, events, invoices, lines)
        random_data: Tuple of (customers, subs, events, invoices, lines)
    
    Returns:
        Combined tuple of DataFrames
    """
    ec_customers, ec_subs, ec_events, ec_invoices, ec_lines = edge_data
    rd_customers, rd_subs, rd_events, rd_invoices, rd_lines = random_data
    
    # Combine lists
    all_customers = ec_customers + rd_customers
    all_subs = ec_subs + rd_subs
    all_events = ec_events + rd_events
    all_invoices = ec_invoices + rd_invoices
    all_lines = ec_lines + rd_lines
    
    # Convert to DataFrames
    customers_df = pd.DataFrame(all_customers)
    subs_df = pd.DataFrame(all_subs)
    events_df = pd.DataFrame(all_events)
    invoices_df = pd.DataFrame(all_invoices)
    lines_df = pd.DataFrame(all_lines)
    
    return customers_df, subs_df, events_df, invoices_df, lines_df


def main():
    """Main execution function."""
    # Parse arguments
    parser = argparse.ArgumentParser(description='Generate subscription data')
    parser.add_argument('--edge-cases-only', action='store_true',
                        help='Generate only deterministic edge cases')
    parser.add_argument('--random-only', action='store_true',
                        help='Generate only random data')
    args = parser.parse_args()
    
    # Use config loaded from utils
    config = CONFIG
    
    # Set random seed for reproducibility - ensures the same "random" data is generated
    # each time the script runs with the same seed value, making results predictable and debuggable
    np.random.seed(config['seed'])  # Modifies NumPy's internal random state
    Faker.seed(config['seed'])  # Modifies Faker's internal random state
    
    print("=" * 60)
    print("SUBSCRIPTION DATA GENERATOR")
    print("=" * 60)
    print(f"\nSeed: {config['seed']}")
    print(f"Date range: {config['date_range']['start_date']} to {config['date_range']['end_date']}")
    print(f"Output: {config['output_dir']}/")
    
    # Generate plans
    print("\n1. Generating plans...")
    plans_df = generate_plans_df(config)
    print(f"   Created {len(plans_df)} plans")
    
    # Generate edge cases
    if not args.random_only:
        print("\n2. Generating deterministic edge cases (S001-S018)...")
        edge_data = generate_all_edge_cases()
        ec_customers, ec_subs, ec_events, ec_invoices, ec_lines = edge_data
        print(f"   Created {len(ec_customers)} test customers")
        print(f"   Created {len(ec_subs)} test subscriptions")
        print(f"   Created {len(ec_events)} test events")
        print(f"   Created {len(ec_invoices)} test invoices")
        print(f"   Created {len(ec_lines)} test invoice lines")
    else:
        edge_data = ([], [], [], [], [])
    
    # Generate random data
    if not args.edge_cases_only:
        print("\n3. Generating random bulk data...")
        random_data = generate_all_random_data(config)
        rd_customers, rd_subs, rd_events, rd_invoices, rd_lines = random_data
        print(f"   Created {len(rd_customers)} random customers")
        print(f"   Created {len(rd_subs)} random subscriptions")
        print(f"   Created {len(rd_events)} random events")
        print(f"   Created {len(rd_invoices)} random invoices")
        print(f"   Created {len(rd_lines)} random invoice lines")
    else:
        random_data = ([], [], [], [], [])
    
    # Combine data
    print("\n4. Combining data...")
    customers_df, subs_df, events_df, invoices_df, lines_df = combine_data(
        edge_data, random_data
    )
    
    # Summary
    print(f"\n   Total customers: {len(customers_df)}")
    print(f"   Total subscriptions: {len(subs_df)}")
    print(f"   Total events: {len(events_df)}")
    print(f"   Total invoices: {len(invoices_df)}")
    print(f"   Total invoice lines: {len(lines_df)}")
    
    # Save to CSV
    print("\n5. Saving CSV files...")
    dataframes = {
        'raw_customers.csv': customers_df,
        'raw_plans.csv': plans_df,
        'raw_subscriptions.csv': subs_df,
        'raw_subscription_events.csv': events_df,
        'raw_invoices.csv': invoices_df,
        'raw_invoice_lines.csv': lines_df
    }
    save_to_csv(dataframes, config['output_dir'])
    
    # Done
    print("\n" + "=" * 60)
    print("✅ DATA GENERATION COMPLETE!")
    print("=" * 60)
    
    # Print edge case summary
    if not args.random_only:
        print("\nDeterministic test cases included:")
        print("   S001: Monthly happy path")
        print("   S002: Annual happy path")
        print("   S003: First-month churn")
        print("   S004: Long-tenure churn")
        print("   S005: Monthly upgrade (prorated) - credit=-20, charge=+40")
        print("   S006: Monthly upgrade near end - credit=-3, charge=+6")
        print("   S007: Annual upgrade (prorated) - credit=-225, charge=+450")
        print("   S008: Two upgrades in one term")
        print("   S009: Monthly downgrade (next renewal)")
        print("   S010: Annual downgrade (next renewal)")
        print("   S011: Pause/resume")
        print("   S012: Pause then cancel")
        print("   S013: Cancel → reactivate")
        print("   S014: Payment failed → recovered")
        print("   S015: Missing invoice")
        print("   S016: Adjustment line (-5)")
        print("   S017: Starts at boundary (Jan 31)")
        print("   S018: Annual mid-start + upgrade")
    
    print(f"\nOutput directory: {config['output_dir']}/")
    print("\nNext steps:")
    print("   1. Load CSVs into your warehouse (BigQuery/Snowflake/DuckDB)")
    print("   2. Run dbt models: dbt run")
    print("   3. Run dbt tests: dbt test")


if __name__ == '__main__':
    main()
