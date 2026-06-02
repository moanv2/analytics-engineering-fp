with locations as (

    select * from {{ ref('stg_locations') }}

)

select
    location_id,
    location_sk,
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
