with source as (

    select * from {{ source('raw', 'raw_subscription_events') }}

),

renamed as (

    select
        -- Primary key
        event_id,

        -- Foreign keys
        subscription_id,
        customer_id,

        -- Event details
        event_type,
        old_plan_id,
        new_plan_id,
        reason,

        -- Timestamps
        cast(occurred_at as timestamp) as occurred_at,
        cast(effective_date as date) as effective_date,

        -- Derived fields
        case
            when event_type = 'plan_changed' and new_plan_id is not null then true
            else false
        end as is_plan_change,

        case
            when event_type in ('canceled', 'churned') then true
            else false
        end as is_churn_event,

        case
            when event_type = 'created' then true
            else false
        end as is_activation_event

    from source

)

select * from renamed
