-- Test: plan_changed Events Have Both Plan IDs
-- =============================================================================
-- Business Rule: When event_type = 'plan_changed', both old_plan_id and 
-- new_plan_id must be populated. Missing values indicate incomplete event data.
-- 
-- This test finds plan_changed events where either plan ID is null.
-- Should return 0 rows.
-- =============================================================================

select
    event_id,
    subscription_id,
    event_type,
    old_plan_id,
    new_plan_id
from {{ ref('fct_subscription_events') }}
where event_type = 'plan_changed'
  and (old_plan_id is null or new_plan_id is null)
