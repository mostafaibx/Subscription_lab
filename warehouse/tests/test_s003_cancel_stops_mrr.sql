-- Test: S003 Cancel Stops MRR
-- =============================================================================
-- Scenario: S003 is a first-month churn subscription.
-- Start: 2025-01-01, Cancel: 2025-01-20
-- Expected: MRR = 0 on and after 2025-01-20 (cancel effective date).
-- 
-- This test finds any day after cancel where MRR > 0.
-- Should return 0 rows if cancellation logic is correct.
-- =============================================================================

select
    date_day,
    subscription_id,
    daily_status,
    mrr
from {{ ref('fct_mrr_daily') }}
where subscription_id = 'S003'
  and date_day >= '2025-01-20'  -- Cancel date from edge_cases.py
  and mrr > 0
