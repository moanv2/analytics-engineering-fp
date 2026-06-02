with risk_flags as (

    select * from {{ ref('int_weather_risk_flags') }}

)

select
    city_day_weather_sk,
    location_id,
    weather_date,
    temperature_2m_max,
    temperature_2m_min,
    temperature_2m_mean,
    precipitation_sum,
    rain_sum,
    snowfall_sum,
    wind_speed_10m_max,
    temp_range_c,
    avg_european_aqi,
    max_european_aqi,
    avg_pm10,
    avg_pm2_5,
    is_hot_day,
    is_rainy_day,
    is_windy_day,
    is_poor_air_day,
    is_comfortable_day,
    daily_risk_score,
    extracted_at
from risk_flags
