with weather as (

    select * from {{ ref('fct_city_weather_day') }}

),

locations as (

    select * from {{ ref('dim_location') }}

)

select
    weather.city_day_weather_sk,
    weather.location_id,
    locations.city_name,
    locations.country,
    locations.country_code,
    locations.admin1,
    locations.latitude,
    locations.longitude,
    locations.elevation,
    locations.population,
    weather.weather_date                 as date_day,
    weather.temperature_2m_max,
    weather.temperature_2m_min,
    weather.temperature_2m_mean,
    weather.precipitation_sum,
    weather.rain_sum,
    weather.snowfall_sum,
    weather.wind_speed_10m_max,
    weather.temp_range_c,
    weather.avg_european_aqi,
    weather.max_european_aqi,
    weather.avg_pm10,
    weather.avg_pm2_5,
    weather.is_hot_day,
    weather.is_rainy_day,
    weather.is_windy_day,
    weather.is_poor_air_day,
    weather.is_comfortable_day,
    weather.daily_risk_score
from weather
inner join locations
    on weather.location_id = locations.location_id
