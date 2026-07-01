-- =========================================================================
-- dim_location  v1   (DEPRECATED — deprecation_date 2026-12-31)
-- -------------------------------------------------------------------------
-- The original location dimension: 11 columns, no elevation_band. Kept only
-- so any consumer still pinned to `ref('dim_location', v=1)` keeps working
-- during the migration window. New consumers should use v2 (dim_location.sql).
-- dbt emits a deprecation warning for anything still on v1 past the date.
-- =========================================================================

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
        population

    from locations

)

select * from final
