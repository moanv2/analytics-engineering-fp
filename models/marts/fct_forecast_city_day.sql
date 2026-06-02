with forecast as (

    select * from {{ ref('stg_forecast_daily') }}

)

select
    forecast_daily_sk,
    location_id,
    city_name,
    country_code,
    forecast_date,
    temperature_2m_max,
    temperature_2m_min,
    temperature_2m_mean,
    precipitation_sum,
    rain_sum,
    snowfall_sum,
    wind_speed_10m_max,
    extracted_at as forecast_extracted_at
from forecast
