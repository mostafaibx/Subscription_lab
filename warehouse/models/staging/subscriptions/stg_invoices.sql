with source as (

    select * from {{ source('raw', 'raw_invoices') }}

),

renamed as (

    select
        -- Primary key
        invoice_id,

        -- Foreign keys
        subscription_id,
        customer_id,

        -- Invoice details
        status as invoice_status,
        currency,
        total_amount,

        -- Timestamps
        cast(issued_at as timestamp) as issued_at,
        cast(paid_at as timestamp) as paid_at,

        -- Period dates
        cast(invoice_period_start as date) as invoice_period_start,
        cast(invoice_period_end as date) as invoice_period_end,

        -- Derived fields
        case 
            when status = 'paid' then true 
            else false 
        end as is_paid,

        case 
            when status = 'uncollectible' then true 
            else false 
        end as is_uncollectible,

        -- Days between issue and payment
        case 
            when paid_at is not null then 
                {{ datediff("issued_at", "paid_at", "day") }}
            else null 
        end as days_to_payment

    from source

)

select * from renamed
