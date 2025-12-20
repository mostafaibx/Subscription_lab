with source as (

    select * from {{ source('raw', 'raw_invoice_lines') }}

),

renamed as (

    select
        -- Primary key
        invoice_line_id,

        -- Foreign keys
        invoice_id,
        subscription_id,
        customer_id,
        plan_id,

        -- Line details
        line_type,
        amount,
        quantity,
        description,

        -- Period dates
        cast(service_period_start as date) as service_period_start,
        cast(service_period_end as date) as service_period_end,

        -- Derived fields
        case
            when line_type = 'recurring_charge' then true
            else false
        end as is_recurring,

        case
            when line_type in ('proration_credit', 'proration_charge') then true
            else false
        end as is_proration,

        case
            when line_type = 'adjustment' then true
            else false
        end as is_adjustment,

        case
            when amount < 0 then true
            else false
        end as is_credit

    from source

)

select * from renamed
