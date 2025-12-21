with source as (

    select * from {{ source('raw', 'raw_subscriptions') }}

),

renamed as (
    select
        -- Primary key
        subscription_id,

        -- Foreign keys
        customer_id,
        plan_id,

        -- Status
        status,
        auto_renew,

        -- Timestamps
        cast(start_at as timestamp) as started_at,
        cast(canceled_at as timestamp) as canceled_at,
        cast(pause_start_at as timestamp) as paused_at,
        cast(pause_end_at as timestamp) as resumed_at,
        cast(created_at as timestamp) as created_at,

        -- Period dates
        cast(current_period_start as date) as current_period_start,
        cast(current_period_end as date) as current_period_end,

        -- Derived fields
        case 
            when status = 'canceled' then true 
            else false 
        end as is_canceled,

        case 
            when status = 'active' and auto_renew = true then true 
            else false 
        end as is_active_recurring

    from source

)

select * from renamed
