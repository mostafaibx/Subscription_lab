{{ config(materialized='view') }}

{# Calculate date bounds in a single query to avoid multiple scans of the subscriptions table #}

{% set date_bounds_query %}
    select
        coalesce(min(started_at)::date, current_date) as min_date,
        coalesce(max(coalesce(current_period_end, canceled_at, started_at))::date, current_date) as max_date
    from {{ ref('stg_subscriptions') }}
{% endset %}

{% set results = run_query(date_bounds_query) %}

{% if execute %}
    {% set start_date = results.columns[0][0] %}
    {% set end_date = results.columns[1][0] %}
{% else %}
    {% set start_date = '2020-01-01' %}
    {% set end_date = 'current_date' %}
{% endif %}

with date_range as (
    select
        generate_series('{{ start_date }}'::date, '{{ end_date }}'::date, interval '1 day')::date as date_day
)

select
    date_day,
    date_trunc('month', date_day)::date as month_start,
    (date_trunc('month', date_day)::date + interval '1 month' - interval '1 day')::date as month_end,
    extract(year from date_day)::int as year,
    extract(month from date_day)::int as month
from date_range