{{ config(materialized='view') }}

with monthly as (
    select
        customer_id,
        month,
        mrr_start,
        mrr_end
    from {{ ref('int_nrr_base_monthly') }}
),
classified as (
    select
        customer_id,
        month,
        mrr_start,
        mrr_end,
        (mrr_end - mrr_start) as mrr_delta,
        case
            when mrr_start = 0 and mrr_end > 0 then 'new'
            when mrr_start > 0 and mrr_end = 0 then 'churn'
            when mrr_start > 0 and mrr_end > 0 and mrr_end > mrr_start then 'expansion'
            when mrr_start > 0 and mrr_end > 0 and mrr_end < mrr_start then 'contraction'
            when mrr_start > 0 and mrr_end > 0 and mrr_end = mrr_start then 'retained'
            else 'no_mrr'
        end as movement_type
    from monthly
)

select
    customer_id,
    month,
    mrr_start,
    mrr_end,
    mrr_delta,
    movement_type
from classified
order by customer_id, month;

