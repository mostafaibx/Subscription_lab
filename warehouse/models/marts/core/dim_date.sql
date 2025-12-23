{{ config(materialized='table') }}

with source as (
    select
        date_day,
        month_start,
        month_end,
        year,
        month
    from {{ ref('int_date_spine') }}
),

renamed as (
    select
        date_day,
        year,
        month,
        extract(day from date_day)::int as day_of_month,
        month_start as month_start_date,
        month_end as month_end_date,
        -- year_month as integer for easy sorting/filtering (e.g., 202312)
        (year * 100 + month)::int as year_month_int,
        -- month_key as string for display (e.g., '2023-12')
        strftime(date_day, '%Y-%m') as month_key
    from source
),

final as (
    select
        date_day,
        year,
        month,
        day_of_month,
        month_start_date,
        month_end_date,
        year_month_int,
        month_key
    from renamed
)

select * from final
