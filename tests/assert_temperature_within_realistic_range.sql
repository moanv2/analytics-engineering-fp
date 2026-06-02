select *
from {{ ref('fct_city_weather_day') }}
where temperature_2m_max > 60
   or temperature_2m_min < -40
   or temperature_2m_mean > 60
   or temperature_2m_mean < -40
