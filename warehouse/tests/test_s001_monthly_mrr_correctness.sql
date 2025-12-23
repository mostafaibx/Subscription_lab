-- Test: S001 Monthly MRR Correctness
-- =============================================================================
-- Scenario: S001 is a simple monthly active subscription.
-- Plan: Basic Monthly (€30)
-- Start: 2025-01-01
-- Expected: MRR = 30.00 on all active days.
-- 
-- This is the baseline "happy path" test — if this fails, something is
-- fundamentally broken in MRR calculation.
-- Should return 0 rows if MRR is correct.
-- =============================================================================

select
    date_day,
    subscription_id,
    daily_status,
    mrr
from {{ ref('fct_mrr_daily') }}
where subscription_id = 'S001'
  and daily_status = 'active'
  and abs(mrr - 30.0) > 0.01  -- Allow tiny floating-point tolerance
