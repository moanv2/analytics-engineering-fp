select *
from {{ ref('fct_air_quality_city_day') }}
where avg_european_aqi < 0
   or max_european_aqi < 0
