-- Test: S013 Cancel → Reactivate
-- =============================================================================
-- Scenario: S013 is a subscription that cancels then reactivates.
-- Start: 2025-01-01
-- Cancel: 2025-02-10
-- Reactivate: 2025-03-01
-- 
-- Expected:
-- - MRR > 0 before cancel (2025-01-01 to 2025-02-09)
-- - MRR = 0 during canceled window (2025-02-10 to 2025-02-28)
-- - MRR > 0 after reactivation (2025-03-01 onward)
-- 
-- Should return 0 rows if cancel/reactivate logic is correct.
-- =============================================================================

-- Check 1: MRR must be > 0 before cancel
select
    date_day,
    subscription_id,
    daily_status,
    mrr,
    'MRR should be > 0 before cancel' as failure_reason
from {{ ref('fct_mrr_daily') }}
where subscription_id = 'S013'
  and date_day >= '2025-01-01'
  and date_day < '2025-02-10'  -- Before cancel
  and daily_status = 'active'
  and mrr <= 0

union all

-- Check 2: MRR must be 0 during canceled window
select
    date_day,
    subscription_id,
    daily_status,
    mrr,
    'MRR should be 0 during canceled window' as failure_reason
from {{ ref('fct_mrr_daily') }}
where subscription_id = 'S013'
  and date_day >= '2025-02-10'  -- Cancel date
  and date_day < '2025-03-01'   -- Before reactivation
  and mrr > 0

union all

-- Check 3: MRR must be > 0 after reactivation
select
    date_day,
    subscription_id,
    daily_status,
    mrr,
    'MRR should be > 0 after reactivation' as failure_reason
from {{ ref('fct_mrr_daily') }}
where subscription_id = 'S013'
  and date_day >= '2025-03-01'  -- Reactivation date
  and daily_status = 'active'
  and mrr <= 0
