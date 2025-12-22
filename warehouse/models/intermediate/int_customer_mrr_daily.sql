{{ config(materialized='view') }}


{# 
Customer-level MRR aggregation from subscription grain.
Located in intermediate layer as it is a reusable building block
for multiple downstream marts (customer metrics, cohorts, LTV, churn).
#}

with subscription_mrr_daily as (
    select
        date_day,
        customer_id,
        subscription_id,
        mrr
    from {{ ref('int_mrr_contract_daily') }}
),
customer_mrr_aggregated as (
    select
        date_day,
        customer_id,
        sum(mrr) as customer_mrr,
        count(distinct subscription_id) as subscription_count
    from subscription_mrr_daily
    group by date_day, customer_id
),
enriched as (
    select
        date_day,
        customer_id,
        customer_mrr,
        subscription_count,
        case
            when customer_mrr > 0 then true
            else false
        end as has_positive_mrr
    from customer_mrr_aggregated
)

select
    date_day,
    customer_id,
    customer_mrr,
    subscription_count,
    has_positive_mrr
from enriched