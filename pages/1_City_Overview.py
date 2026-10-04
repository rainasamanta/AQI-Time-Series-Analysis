import streamlit as st
import pandas as pd
import plotly.express as px

# Load data (dates are stored as YYYY-MM-DD)
df = pd.read_csv("data/aqi_master_clean.csv")
df['Date'] = pd.to_datetime(df['Date'])

# CPCB bucket order and colors
bucket_order = [
    "Good", "Satisfactory", "Moderate",
    "Poor", "Very Poor", "Severe"
]
bucket_colors = {
    "Good": "#00B050",
    "Satisfactory": "#92D050",
    "Moderate": "#FFFF00",
    "Poor": "#FF7C00",
    "Very Poor": "#FF0000",
    "Severe": "#7030A0"
}

# Title
st.title("City Overview")

# City selector
cities = sorted(df["City"].unique())
selected_city = st.selectbox("Select a City", cities)

# Filter
city_df = df[df["City"] == selected_city].copy()

# Compute metrics
total_days = len(city_df)
mean_aqi = round(city_df["AQI"].mean(), 1)
worst_day = int(city_df["AQI"].max())
best_day = int(city_df["AQI"].min())
unhealthy_days = len(
    city_df[
        city_df["AQI_Bucket"].isin(["Poor", "Very Poor", "Severe"])
    ]
)
unhealthy_pct = round(unhealthy_days / total_days * 100, 1)

# Metric cards
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Days", total_days)
col2.metric("Mean AQI", mean_aqi)
col3.metric("Worst AQI", worst_day)
col4.metric("Best AQI", best_day)

st.divider()

# AQI Trend line
fig_trend = px.line(
    city_df,
    x="Date",
    y="AQI",
    title=f"{selected_city} - Daily AQI Trend"
)
fig_trend.update_traces(line_color="#1f77b4", line_width=1)
fig_trend.update_layout(
    hovermode="x unified",
    xaxis=dict(
        tickformat="%Y",
        hoverformat="%d %b %Y"
    )
)
st.plotly_chart(fig_trend, use_container_width=True)

st.divider()

# Yearly stacked bar chart
yearly_bucket = (
    city_df.groupby(["Year", "AQI_Bucket"])
    .size()
    .reset_index(name="Days")
)

fig_yearly = px.bar(
    yearly_bucket,
    x="Year",
    y="Days",
    color="AQI_Bucket",
    title=f"{selected_city} - Days in Each AQI Category by Year",
    category_orders={"AQI_Bucket": bucket_order},
    color_discrete_map=bucket_colors,
    barmode="stack"
)
fig_yearly.update_layout(
    xaxis=dict(tickmode="linear"),
    legend_title="AQI Category"
)
st.plotly_chart(fig_yearly, use_container_width=True)
st.caption("2025 covers January–March only, so its bar is shorter than the other years.")

st.divider()

# Health exposure summary
st.subheader("Health Exposure Summary")

col_a, col_b = st.columns(2)

with col_a:
    # Bucket donut chart
    bucket_counts = (
        city_df["AQI_Bucket"]
        .value_counts()
        .reindex(bucket_order)
        .dropna()
        .reset_index()
    )
    bucket_counts.columns = ["AQI_Bucket", "Days"]

    fig_donut = px.pie(
        bucket_counts,
        names="AQI_Bucket",
        values="Days",
        hole=0.5,
        color="AQI_Bucket",
        color_discrete_map=bucket_colors,
        title="Overall AQI Distribution"
    )
    fig_donut.update_traces(
        textposition="inside",
        textinfo="percent+label"
    )
    st.plotly_chart(fig_donut, use_container_width=True)

with col_b:
    # Best year: complete years only (2025 has only Jan-Mar)
    days_per_year = city_df.groupby("Year").size()
    complete_years = days_per_year[days_per_year >= 360].index
    yearly_mean = (
        city_df[city_df["Year"].isin(complete_years)]
        .groupby("Year")["AQI"]
        .mean()
    )
    best_year = yearly_mean.idxmin()
    first_year, last_year = min(complete_years), max(complete_years)

    st.markdown("#### At a glance")
    st.markdown(f"""
    - **{total_days}** days of air quality data recorded
    - **{unhealthy_days} days** ({unhealthy_pct}%) with unhealthy air (Poor or worse)
    - **{total_days - unhealthy_days} days** ({round(100 - unhealthy_pct, 1)}%) with acceptable air quality
    - Mean AQI of **{mean_aqi}** falls in the **{"Good" if mean_aqi <= 50 else "Satisfactory" if mean_aqi <= 100 else "Moderate" if mean_aqi <= 200 else "Poor"}** category
    - Best year ({first_year}–{last_year}): **{best_year}**
    """)
