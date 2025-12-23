-- Test: S002 Annual MRR Normalization
-- =============================================================================
-- Scenario: S002 is an annual subscription with Basic Annual plan (€300/year).
-- Expected: MRR = 25.00 (300/12) on all active days.
-- 
-- This test finds any day where S002 is active but MRR ≠ 25.
-- Should return 0 rows if MRR normalization is correct.
-- =============================================================================

select
    date_day,
    subscription_id,
    daily_status,
    mrr
from {{ ref('fct_mrr_daily') }}
where subscription_id = 'S002'
  and daily_status = 'active'
  and abs(mrr - 25.0) > 0.01  -- Allow tiny floating-point tolerance
