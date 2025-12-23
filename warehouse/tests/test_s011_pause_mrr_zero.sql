-- Test: S011 Pause MRR Zero
-- =============================================================================
-- Scenario: S011 has a pause/resume cycle.
-- Pause: 2025-01-15, Resume: 2025-01-29
-- Expected: MRR = 0 during pause window (2025-01-15 to 2025-01-28 inclusive).
--           MRR > 0 before pause and after resume.
-- 
-- This test checks two conditions:
-- 1. MRR = 0 during pause window
-- 2. MRR > 0 on active days outside pause
-- Should return 0 rows if pause logic is correct.
-- =============================================================================

-- Check 1: MRR must be 0 during pause period
select
    date_day,
    subscription_id,
    daily_status,
    mrr,
    'MRR should be 0 during pause' as failure_reason
from {{ ref('fct_mrr_daily') }}
where subscription_id = 'S011'
  and date_day >= '2025-01-15'  -- Pause start
  and date_day < '2025-01-29'   -- Resume date (exclusive, resume happens on this day)
  and mrr > 0

union all

-- Check 2: MRR should be > 0 on active days before pause
select
    date_day,
    subscription_id,
    daily_status,
    mrr,
    'MRR should be > 0 on active days before pause' as failure_reason
from {{ ref('fct_mrr_daily') }}
where subscription_id = 'S011'
  and date_day >= '2025-01-01'  -- Start date
  and date_day < '2025-01-15'   -- Before pause
  and daily_status = 'active'
  and mrr <= 0
