-- Test: S009 Downgrade Effective at Renewal (No Proration)
-- =============================================================================
-- Scenario: S009 is a monthly downgrade that takes effect at next renewal.
-- Plan: Pro Monthly (€60) → Basic Monthly (€30)
-- Start: 2025-01-01
-- Downgrade requested: 2025-01-10
-- Effective: 2025-01-31 (period end / next renewal)
-- 
-- Key difference from upgrades:
-- - Downgrades do NOT prorate mid-cycle
-- - Customer keeps higher plan until renewal
-- - MRR stays at €60 until effective date
-- 
-- Expected:
-- - MRR = 60 from start until 2025-01-30 (before renewal)
-- - MRR = 30 from 2025-01-31 onward (after downgrade effective)
-- 
-- Note: The exact effective date depends on your billing policy.
-- This test checks the principle: MRR shouldn't drop until effective date.
-- Should return 0 rows if downgrade timing is correct.
-- =============================================================================

-- Check: MRR should remain at higher plan until effective date
-- (before 2025-01-31, MRR should be 60, not 30)
select
    date_day,
    subscription_id,
    daily_status,
    mrr,
    'MRR should be 60 before downgrade effective date' as failure_reason
from {{ ref('fct_mrr_daily') }}
where subscription_id = 'S009'
  and date_day >= '2025-01-01'
  and date_day < '2025-01-31'  -- Before effective date (period end)
  and daily_status = 'active'
  and abs(mrr - 60.0) > 0.01   -- Should be Pro price, not Basic
