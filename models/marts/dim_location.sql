-- =========================================================================
-- dim_location  v2   (LATEST — resolved by a bare ref('dim_location'))
-- -------------------------------------------------------------------------
-- The location dimension, evolved. v2 adds elevation_band on top of every v1
-- column, so this is an additive change (v1 consumers are unaffected until
-- they choose to migrate). Because this file is the un-suffixed model file, dbt
-- treats it as the latest_version declared in marts.yml (v2).
--
-- alias='dim_location' keeps the physical table named `dim_location` (not
-- dim_location_v2), so the Streamlit dashboard and any ad-hoc query that reads
-- main.dim_location keep working unchanged.
-- =========================================================================

{{ config(alias='dim_location') }}

with locations as (

    select * from {{ ref('stg_locations') }}

),

final as (

    select
        location_sk,
        location_id,
        city_name,
        country,
        country_code,
        admin1,
        latitude,
        longitude,
        timezone,
        elevation,
        population,
        -- v2 addition: a coarse terrain band derived straight from elevation
        -- (meters). Lets the dashboard group cities by terrain with no extra
        -- join. Null-safe so the not_null contract/test always holds.
        case
            when elevation is null then 'Unknown'
            when elevation < 200 then 'Lowland'
            when elevation < 800 then 'Midland'
            else 'Highland'
        end as elevation_band

    from locations

)

select * from final
