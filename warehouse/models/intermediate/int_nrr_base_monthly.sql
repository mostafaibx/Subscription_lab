{{ config(materialized='view') }}

with customer_mrr_daily as (
    select
        date_day,
        customer_id,
        customer_mrr
    from {{ ref('int_customer_mrr_daily') }}
),
mrr_with_month as (
    select
        date_day,
        customer_id,
        customer_mrr,
        date_trunc('month', date_day)::date as month
    from customer_mrr_daily
),
month_boundaries as (
    select
        customer_id,
        month,
        min(date_day) as month_first_day,
        max(date_day) as month_last_day
    from mrr_with_month
    group by customer_id, month
),
mrr_start as (
    select
        mrr_with_month.customer_id,
        mrr_with_month.month,
        mrr_with_month.customer_mrr as mrr_start
    from mrr_with_month
    inner join month_boundaries
        on mrr_with_month.customer_id = month_boundaries.customer_id
        and mrr_with_month.month = month_boundaries.month
        and mrr_with_month.date_day = month_boundaries.month_first_day
),
mrr_end as (
    select
        mrr_with_month.customer_id,
        mrr_with_month.month,
        mrr_with_month.customer_mrr as mrr_end
    from mrr_with_month
    inner join month_boundaries
        on mrr_with_month.customer_id = month_boundaries.customer_id
        and mrr_with_month.month = month_boundaries.month
        and mrr_with_month.date_day = month_boundaries.month_last_day
),
combined as (
    select
        coalesce(mrr_start.customer_id, mrr_end.customer_id) as customer_id,
        coalesce(mrr_start.month, mrr_end.month) as month,
        coalesce(mrr_start.mrr_start, 0) as mrr_start,
        coalesce(mrr_end.mrr_end, 0) as mrr_end
    from mrr_start
    full outer join mrr_end
        on mrr_start.customer_id = mrr_end.customer_id
        and mrr_start.month = mrr_end.month
)

select
    customer_id,
    month,
    mrr_start,
    mrr_end
from combined
order by customer_id, month;
