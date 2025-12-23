-- Test: S014 Delinquent MRR Zero
-- =============================================================================
-- Scenario: S014 has a payment failure → recovery cycle.
-- Failed: 2025-01-31, Recovered: 2025-02-10
-- Expected: MRR = 0 during delinquent window (2025-01-31 to 2025-02-09).
--           daily_status should be 'delinquent' during this period.
-- 
-- This test finds days in the delinquent window where MRR > 0.
-- Should return 0 rows if delinquent handling is correct.
-- =============================================================================

select
    date_day,
    subscription_id,
    daily_status,
    mrr,
    'MRR should be 0 during delinquent window' as failure_reason
from {{ ref('fct_mrr_daily') }}
where subscription_id = 'S014'
  and date_day >= '2025-01-31'  -- Payment failed date
  and date_day < '2025-02-10'   -- Payment recovered date (exclusive)
  and mrr > 0
