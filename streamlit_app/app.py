import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px

DB_PATH = "data/weather_analytics.duckdb"

st.set_page_config(
    page_title="Spanish City Weather Risk & Comfort Monitor",
    page_icon="🌤️",
    layout="wide",
)

st.title("Spanish City Weather Risk & Comfort Monitor")
st.markdown(
    """
    Powered by **`mart_city_weather_summary`** — one row per city per date.
    Data sourced from the [Open-Meteo API](https://open-meteo.com/).
    """
)


@st.cache_data
def load_data() -> pd.DataFrame:
    con = duckdb.connect(DB_PATH, read_only=True)
    df = con.execute("SELECT * FROM main.mart_city_weather_summary").df()
    con.close()
    df["date_day"] = pd.to_datetime(df["date_day"])
    return df


try:
    df = load_data()
except Exception as e:
    st.error(
        f"Could not connect to the database at `{DB_PATH}`. "
        "Run `python scripts/load_to_duckdb.py` then `dbt build` first.\n\n"
        f"Error: {e}"
    )
    st.stop()

# ── Sidebar filters ────────────────────────────────────────────────────────────
st.sidebar.header("Filters")

all_cities = sorted(df["city_name"].dropna().unique())
selected_cities = st.sidebar.multiselect(
    "Cities",
    all_cities,
    default=all_cities[:10],
)

date_min = df["date_day"].min().date()
date_max = df["date_day"].max().date()
date_range = st.sidebar.date_input(
    "Date range",
    value=(date_min, date_max),
    min_value=date_min,
    max_value=date_max,
)

metric = st.sidebar.selectbox(
    "Metric for trend chart",
    {
        "temperature_2m_mean": "Mean temperature (°C)",
        "precipitation_sum": "Precipitation (mm)",
        "wind_speed_10m_max": "Max wind speed (km/h)",
        "avg_european_aqi": "Avg European AQI",
        "daily_risk_score": "Daily risk score",
    },
    format_func=lambda k: {
        "temperature_2m_mean": "Mean temperature (°C)",
        "precipitation_sum": "Precipitation (mm)",
        "wind_speed_10m_max": "Max wind speed (km/h)",
        "avg_european_aqi": "Avg European AQI",
        "daily_risk_score": "Daily risk score",
    }[k],
)

# ── Filter data ────────────────────────────────────────────────────────────────
if len(date_range) == 2:
    start_date, end_date = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
else:
    start_date, end_date = pd.Timestamp(date_min), pd.Timestamp(date_max)

filtered = df[
    df["city_name"].isin(selected_cities)
    & (df["date_day"] >= start_date)
    & (df["date_day"] <= end_date)
].copy()

if filtered.empty:
    st.warning("No data for the selected filters.")
    st.stop()

# ── KPI cards ──────────────────────────────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Avg temperature",
    f"{filtered['temperature_2m_mean'].mean():.1f} °C",
)
col2.metric(
    "Total rain",
    f"{filtered['precipitation_sum'].sum():.0f} mm",
)
col3.metric(
    "Avg AQI",
    f"{filtered['avg_european_aqi'].mean():.1f}"
    if filtered["avg_european_aqi"].notna().any()
    else "N/A",
)
col4.metric(
    "Risky days",
    int((filtered["daily_risk_score"] > 0).sum()),
)
best_city = (
    filtered.groupby("city_name")["is_comfortable_day"]
    .sum()
    .idxmax()
)
col5.metric("Most comfortable city", best_city)

st.divider()

# ── City risk ranking bar chart ────────────────────────────────────────────────
st.subheader("City risk & comfort ranking")

city_rank = (
    filtered.groupby("city_name", as_index=False)
    .agg(
        avg_risk_score=("daily_risk_score", "mean"),
        comfortable_days=("is_comfortable_day", "sum"),
        avg_aqi=("avg_european_aqi", "mean"),
        avg_temp=("temperature_2m_mean", "mean"),
    )
    .sort_values("avg_risk_score", ascending=False)
)

tab_risk, tab_comfort = st.tabs(["Risk ranking", "Comfort days"])

with tab_risk:
    fig = px.bar(
        city_rank.sort_values("avg_risk_score", ascending=False),
        x="city_name",
        y="avg_risk_score",
        color="avg_risk_score",
        color_continuous_scale="Reds",
        labels={"city_name": "City", "avg_risk_score": "Avg risk score"},
        title="Average Daily Risk Score by City",
        custom_data=["city_name", "avg_risk_score"],
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Avg Daily Risk Score: %{customdata[1]:.2f}"
            "<extra></extra>"
        )
    )
    fig.update_layout(xaxis_tickangle=-45, coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

with tab_comfort:
    fig = px.bar(
        city_rank.sort_values("comfortable_days", ascending=False),
        x="city_name",
        y="comfortable_days",
        color="comfortable_days",
        color_continuous_scale="Greens",
        labels={"city_name": "City", "comfortable_days": "Comfortable days"},
        title="Total comfortable days by city",
        custom_data=["city_name", "comfortable_days"]
    )
    fig.update_traces(
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Comfortable days: %{customdata[1]:.2f}"
            "<extra></extra>"
        )
    )
    fig.update_layout(coloraxis_showscale=False, xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

# ── Daily trend line ───────────────────────────────────────────────────────────
st.subheader("Daily trend")

metric_labels = {
    "temperature_2m_mean": "Mean temperature (°C)",
    "precipitation_sum": "Precipitation (mm)",
    "wind_speed_10m_max": "Max wind speed (km/h)",
    "avg_european_aqi": "Avg European AQI",
    "daily_risk_score": "Daily risk score",
}

trend = (
    filtered.groupby(["date_day", "city_name"], as_index=False)[metric]
    .mean()
)

fig = px.line(
    trend,
    x="date_day",
    y=metric,
    color="city_name",
    labels={"date_day": "Date", metric: metric_labels[metric], "city_name": "City"},
    title=f"{metric_labels[metric]} over time",
    custom_data=["city_name", "date_day", metric],
)

fig.update_traces(
    hovertemplate=(
        "<b>%{customdata[0]}</b><br>"
        "Date: %{customdata[1]|%Y-%m-%d}<br>"
        f"{metric_labels[metric]}: " + "%{customdata[2]:.2f}"
        "<extra></extra>"
    )
)
fig.update_layout(
    hovermode="closest",
    xaxis_title="Date",
    yaxis_title=metric_labels[metric],
    legend_title="City",
)
st.plotly_chart(fig, use_container_width=True)

# ── Map ────────────────────────────────────────────────────────────────────────
st.subheader("Geographic view — latest day per city")

latest = (
    filtered.sort_values("date_day")
    .groupby("city_name", as_index=False)
    .last()
)

# ensure size column has no nulls for scatter_mapbox
latest["plot_size"] = (latest["daily_risk_score"] + 0.5).fillna(0.5)

fig = px.scatter_mapbox(
    latest,
    lat="latitude",
    lon="longitude",
    color="daily_risk_score",
    size="plot_size",
    hover_name="city_name",
    custom_data=["city_name", "daily_risk_score", "temperature_2m_mean", "avg_european_aqi"],
    color_continuous_scale="RdYlGn_r",
    zoom=5,
    center={"lat": 40.0, "lon": -3.5},
    height=500,
    title="Daily risk score by city (latest date)",
)

fig.update_traces(
    hovertemplate=(
        "<b>%{customdata[0]}</b><br>"
        "Risk score: %{customdata[1]:.2f}<br>"
        "Avg temperature: %{customdata[2]:.1f} °C<br>"
        "Avg AQI: %{customdata[3]:.1f}"
        "<extra></extra>"
    )
)
fig.update_layout(
    mapbox_style="open-street-map",
    coloraxis_colorbar=dict(title="Risk score"),
)
st.plotly_chart(fig, use_container_width=True)

# ── Top 10 worst city-days ─────────────────────────────────────────────────────
st.subheader("Top 10 highest-risk city-days")

worst = (
    filtered[
        [
            "city_name",
            "date_day",
            "daily_risk_score",
            "temperature_2m_max",
            "precipitation_sum",
            "wind_speed_10m_max",
            "avg_european_aqi",
            "is_hot_day",
            "is_rainy_day",
            "is_windy_day",
            "is_poor_air_day",
        ]
    ]
    .sort_values("daily_risk_score", ascending=False)
    .head(10)
    .reset_index(drop=True)
)
worst["date_day"] = worst["date_day"].dt.date
worst.index += 1
worst.columns = [
    "City",
    "Date",
    "Risk Score",
    "Max Temp (°C)",
    "Precipitation (mm)",
    "Max Wind (km/h)",
    "Avg AQI",
    "Hot Day",
    "Rainy Day",
    "Windy Day",
    "Poor Air Day",
]
st.dataframe(worst, use_container_width=True)
