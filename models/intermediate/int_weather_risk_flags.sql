with weather as (

    select * from {{ ref('int_city_day_weather') }}

),

air_quality as (

    select * from {{ ref('int_air_quality_daily') }}

),

joined as (

    select
        weather.*,
        air_quality.avg_european_aqi,
        air_quality.max_european_aqi,
        air_quality.avg_pm10,
        air_quality.avg_pm2_5
    from weather
    left join air_quality
        on weather.location_id = air_quality.location_id
        and weather.weather_date = air_quality.air_quality_date

),

flagged as (

    select
        *,
        case when temperature_2m_max >= 30 then 1 else 0 end           as is_hot_day,
        case when precipitation_sum >= 5 then 1 else 0 end              as is_rainy_day,
        case when wind_speed_10m_max >= 30 then 1 else 0 end            as is_windy_day,
        case when coalesce(avg_european_aqi, 0) >= 50 then 1 else 0 end as is_poor_air_day,

        case
            when temperature_2m_mean between 18 and 26
             and coalesce(precipitation_sum, 0) < 1
             and coalesce(wind_speed_10m_max, 0) < 25
             and coalesce(avg_european_aqi, 0) < 50
            then 1 else 0
        end as is_comfortable_day,

        (
            case when temperature_2m_max >= 30 then 1 else 0 end +
            case when precipitation_sum >= 5 then 1 else 0 end +
            case when wind_speed_10m_max >= 30 then 1 else 0 end +
            case when coalesce(avg_european_aqi, 0) >= 50 then 1 else 0 end
        ) as daily_risk_score

    from joined

)

select * from flagged
