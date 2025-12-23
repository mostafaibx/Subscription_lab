-- Test: S005 Proration Pairing
-- =============================================================================
-- Scenario: S005 is a mid-cycle upgrade (Basic→Pro on 2025-01-11).
-- Expected: Invoice lines must include:
--   - At least 1 proration_credit (amount ≤ 0)
--   - At least 1 proration_charge (amount ≥ 0)
-- 
-- This test returns a row if proration pairing is broken.
-- Should return 0 rows if proration handling is correct.
-- =============================================================================

with proration_summary as (
    select
        sum(case when line_type = 'proration_credit' then 1 else 0 end) as credit_count,
        sum(case when line_type = 'proration_charge' then 1 else 0 end) as charge_count,
        sum(case when line_type = 'proration_credit' and amount > 0 then 1 else 0 end) as bad_credit_sign,
        sum(case when line_type = 'proration_charge' and amount < 0 then 1 else 0 end) as bad_charge_sign
    from {{ ref('fct_invoice_lines') }}
    where subscription_id = 'S005'
)

select
    'S005' as subscription_id,
    credit_count,
    charge_count,
    bad_credit_sign,
    bad_charge_sign,
    case 
        when credit_count = 0 then 'Missing proration_credit'
        when charge_count = 0 then 'Missing proration_charge'
        when bad_credit_sign > 0 then 'proration_credit has positive amount'
        when bad_charge_sign > 0 then 'proration_charge has negative amount'
        else 'Unknown error'
    end as failure_reason
from proration_summary
where credit_count = 0
   or charge_count = 0
   or bad_credit_sign > 0
   or bad_charge_sign > 0
