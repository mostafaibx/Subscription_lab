with source as (

    select * from {{ source('raw', 'raw_customers') }}

),

renamed as (

    select
        -- Primary key
        customer_id,

        -- Attributes
        customer_name,
        customer_segment,
        country,
        is_test_account,

        -- Timestamps
        cast(created_at as timestamp) as created_at

    from source

)

select * from renamed
