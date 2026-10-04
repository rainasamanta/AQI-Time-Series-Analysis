import streamlit as st
import pandas as pd
import plotly.express as px

# Load data (dates are stored as YYYY-MM-DD)
df = pd.read_csv("data/aqi_master_clean.csv")
df['Date'] = pd.to_datetime(df['Date'])

# Month name mapping
month_names = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr",
    5: "May", 6: "Jun", 7: "Jul", 8: "Aug",
    9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
}

st.title("Seasonal Exposure Patterns")
st.markdown("Discover which months carry the highest and lowest air quality risk.")

st.divider()

# City selector
cities = sorted(df["City"].unique())
selected_city = st.selectbox("Select a City", cities)

city_df = df[df["City"] == selected_city].copy()
city_df["Month_Num"] = city_df["Date"].dt.month
city_df["Month"] = city_df["Month_Num"].map(month_names)
city_df["Year"] = city_df["Date"].dt.year

st.divider()

# Monthly averages
monthly_avg = (
    city_df.groupby("Month_Num")["AQI"]
    .mean()
    .reset_index()
)
monthly_avg["Month"] = monthly_avg["Month_Num"].map(month_names)

safest_row = monthly_avg.loc[monthly_avg["AQI"].idxmin()]
dangerous_row = monthly_avg.loc[monthly_avg["AQI"].idxmax()]

safest_month = safest_row["Month"]
safest_aqi = round(safest_row["AQI"], 1)
dangerous_month = dangerous_row["Month"]
dangerous_aqi = round(dangerous_row["AQI"], 1)

# Callout cards
st.subheader("Key Months at a Glance")

col1, col2 = st.columns(2)

with col1:
    st.success(f"""
    ### Safest Month to Visit
    **{safest_month}**
    Average AQI: **{safest_aqi}**

    Historically the cleanest month in {selected_city}.
    """)

with col2:
    st.error(f"""
    ### Most Dangerous Month
    **{dangerous_month}**
    Average AQI: **{dangerous_aqi}**

    Historically the most polluted month in {selected_city}.
    """)

st.divider()

# Heatmap - rows = years, columns = months
st.subheader("Monthly AQI Heatmap (2019–2025)")
st.caption("Color intensity shows mean AQI - darker red means worse air quality. 2025 covers January–March only.")

heatmap_data = (
    city_df.groupby(["Year", "Month_Num"])["AQI"]
    .mean()
    .reset_index()
)

heatmap_pivot = heatmap_data.pivot(
    index="Year",
    columns="Month_Num",
    values="AQI"
)

# Rename columns to month names
heatmap_pivot.columns = [
    month_names[m] for m in heatmap_pivot.columns
]

fig_heatmap = px.imshow(
    heatmap_pivot,
    color_continuous_scale="RdYlGn_r",
    aspect="auto",
    title=f"{selected_city} - Mean AQI by Month and Year",
    labels={"color": "Mean AQI"},
    text_auto=".0f"
)
fig_heatmap.update_layout(
    xaxis_title="Month",
    yaxis_title="Year",
    coloraxis_colorbar=dict(title="AQI"),
    yaxis=dict(tickmode="linear")
)
st.plotly_chart(fig_heatmap, use_container_width=True)
