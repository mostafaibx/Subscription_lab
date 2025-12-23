-- Test: Invoice Totals Reconcile
-- =============================================================================
-- Business Rule: For every invoice, the total_amount must equal the sum of its
-- line item amounts.
-- 
-- This test finds invoices where abs(total_amount - sum(lines)) > 0.01.
-- Should return 0 rows if invoice totals are consistent.
-- =============================================================================

with invoice_line_totals as (
    select
        invoice_id,
        sum(amount) as lines_total
    from {{ ref('fct_invoice_lines') }}
    group by invoice_id
),

invoice_headers as (
    select
        invoice_id,
        total_amount
    from {{ ref('stg_invoices') }}
),

comparison as (
    select
        h.invoice_id,
        h.total_amount as invoice_total,
        coalesce(l.lines_total, 0) as lines_total,
        abs(h.total_amount - coalesce(l.lines_total, 0)) as diff
    from invoice_headers h
    left join invoice_line_totals l on h.invoice_id = l.invoice_id
)

select
    invoice_id,
    invoice_total,
    lines_total,
    diff
from comparison
where diff > 0.01
