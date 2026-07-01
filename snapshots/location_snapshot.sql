-- =========================================================================
-- SNAPSHOT  (SCD Type 2 — slowly changing dimension history)
-- -------------------------------------------------------------------------
-- Source   : open_meteo.raw_locations  (one row per city)
-- Grain    : one row per city per *version* of that city's metadata
-- Job      : keep a full history of how a city's descriptive attributes
--            change over time. A plain model would overwrite yesterday's
--            values; a snapshot preserves them with dbt_valid_from /
--            dbt_valid_to windows, so we can always answer "what did we know
--            about Madrid's population/elevation on date X?".
-- Strategy : 'check' — the Geocoding API gives us no reliable per-row
--            "updated_at", so we cannot use the 'timestamp' strategy. Instead
--            dbt diffs the columns in check_cols on every run and opens a new
--            record only when one of them actually changes.
-- Run with : `dbt snapshot`  (also runs as part of `dbt build`)
-- Note     : incremental models track fast-moving *facts*; snapshots track
--            slow-moving *dimensions* that need an audit trail. This is the
--            dimension counterpart to the incremental fct_forecast_city_day.
-- =========================================================================

{% snapshot location_snapshot %}

{{
    config(
        target_schema='snapshots',
        unique_key='location_id',
        strategy='check',
        check_cols=['city_name', 'country', 'admin1', 'population', 'elevation', 'timezone']
    )
}}

-- Select straight from the raw source (snapshots sit beside staging, not
-- downstream of it) so we capture the source of truth before any transform.
select
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
    extracted_at
from {{ source('open_meteo', 'raw_locations') }}

{% endsnapshot %}
