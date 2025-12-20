with source as (

    select * from {{ source('raw', 'raw_plans') }}

),

renamed as (

    select
        -- Primary key
        plan_id,

        -- Attributes
        plan_name,
        currency,
        billing_period_months,
        price_per_period,
        mrr_equivalent,
        is_active,

        -- Derived
        case 
            when billing_period_months = 1 then 'monthly'
            when billing_period_months = 12 then 'annual'
            else 'other'
        end as billing_frequency

    from source

)

select * from renamed
