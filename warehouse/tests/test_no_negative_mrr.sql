-- Test: No Negative MRR
-- =============================================================================
-- Business Rule: MRR can never be negative. Zero is valid (paused, canceled,
-- delinquent), but negative values indicate a bug.
-- 
-- This test finds any row in fct_mrr_daily where MRR < 0.
-- Should return 0 rows.
-- 
-- Note: This is also enforced via schema test (expression_is_true >= 0),
-- but having a singular test makes debugging easier if it fails.
-- =============================================================================

select
    date_day,
    subscription_id,
    customer_id,
    daily_status,
    mrr
from {{ ref('fct_mrr_daily') }}
where mrr < 0
