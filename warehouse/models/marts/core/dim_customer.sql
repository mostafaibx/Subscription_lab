{{ config(materialized='table') }}

with customers as (
    select
        customer_id,
        customer_name,
        customer_segment,
        country,
        created_at,
        is_test_account
    from {{ ref('stg_customers') }}
),

first_paid as (
    select
        customer_id,
        first_paid_date,
        first_paid_month
    from {{ ref('int_first_paid_date') }}
),

joined as (
    select
        customers.customer_id,
        customers.customer_name,
        customers.customer_segment,
        customers.country,
        customers.created_at,
        customers.is_test_account,
        first_paid.first_paid_date,
        first_paid.first_paid_month
    from customers
    left join first_paid
        on customers.customer_id = first_paid.customer_id
),

final as (
    select
        customer_id,
        customer_name,
        customer_segment,
        country,
        created_at,
        is_test_account,
        first_paid_date,
        first_paid_month
    from joined
)

select * from final
