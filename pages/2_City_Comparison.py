import streamlit as st
import pandas as pd
import plotly.express as px

# Load data (dates are stored as YYYY-MM-DD)
df = pd.read_csv("data/aqi_master_clean.csv")
df['Date'] = pd.to_datetime(df['Date'])

# Bucket setup
bucket_order = [
    "Good", "Satisfactory", "Moderate",
    "Poor", "Very Poor", "Severe"
]

st.title("City vs City - Health Burden Comparison")
st.markdown("Compare the cumulative air quality between two cities.")

st.divider()

# City selectors - prevent same city being selected twice
cities = sorted(df["City"].unique())

col1, col2 = st.columns(2)
with col1:
    city_a = st.selectbox("Select City A", cities, index=0)
with col2:
    remaining = [c for c in cities if c != city_a]
    city_b = st.selectbox("Select City B", remaining, index=0)

# Filter
df_a = df[df["City"] == city_a].copy().sort_values("Date")
df_b = df[df["City"] == city_b].copy().sort_values("Date")

# Compute unhealthy days
def unhealthy(city_df):
    return city_df[
        city_df["AQI_Bucket"].isin(["Poor", "Very Poor", "Severe"])
    ]

unhealthy_a = len(unhealthy(df_a))
unhealthy_b = len(unhealthy(df_b))
total_a = len(df_a)
total_b = len(df_b)

# Compare percentages, since cities have slightly different numbers of recorded days
pct_a = round(unhealthy_a / total_a * 100, 1)
pct_b = round(unhealthy_b / total_b * 100, 1)

st.divider()

# Headline verdict
st.subheader("The Verdict")
if pct_a == pct_b:
    st.info(
        f"**{city_a}** and **{city_b}** had unhealthy air on the same share of days "
        f"(**{pct_a}%**) over the recorded period."
    )
else:
    worse_city, worse_pct = (city_a, pct_a) if pct_a > pct_b else (city_b, pct_b)
    better_city, better_pct = (city_b, pct_b) if pct_a > pct_b else (city_a, pct_a)
    st.error(
        f"**{worse_city}** had unhealthy air on **{worse_pct}%** of days, "
        f"compared with **{better_pct}%** in **{better_city}** over the recorded period."
    )

st.divider()

# Metric cards
st.subheader("Head to Head")

m1, m2, m3, m4 = st.columns(4)
m1.metric(
    f"{city_a} - Mean AQI",
    round(df_a["AQI"].mean(), 1),
    delta=round(df_a["AQI"].mean() - df_b["AQI"].mean(), 1),
    delta_color="inverse"
)
m2.metric(
    f"{city_b} - Mean AQI",
    round(df_b["AQI"].mean(), 1)
)
m3.metric(
    f"{city_a} - Unhealthy Days",
    f"{unhealthy_a} ({pct_a}%)",
)
m4.metric(
    f"{city_b} - Unhealthy Days",
    f"{unhealthy_b} ({pct_b}%)",
)

st.caption("Unhealthy days = days with AQI classified as Poor, Very Poor, or Severe (AQI > 200) as per CPCB standards.")
st.divider()

# Bucket breakdown comparison
st.subheader("AQI Category Breakdown")
st.caption("What percentage of days did each city spend in each pollution category?")

def bucket_pct(city_df, city_name):
    counts = (
        city_df["AQI_Bucket"]
        .value_counts(normalize=True)
        .mul(100)
        .round(1)
        .reindex(bucket_order)
        .fillna(0)
        .reset_index()
    )
    counts.columns = ["AQI_Bucket", "Percentage"]
    counts["City"] = city_name
    return counts

combined = pd.concat([
    bucket_pct(df_a, city_a),
    bucket_pct(df_b, city_b)
])

fig_bucket = px.bar(
    combined,
    x="AQI_Bucket",
    y="Percentage",
    color="City",
    barmode="group",
    category_orders={"AQI_Bucket": bucket_order},
    title="% Days in Each AQI Category",
    labels={"Percentage": "% of Days"}
)
st.plotly_chart(fig_bucket, use_container_width=True)

st.divider()

# Summary verdict cards
st.subheader("City Report Cards")

card_a, card_b = st.columns(2)

with card_a:
    st.markdown(f"#### {city_a}")
    st.markdown(f"""
    - Mean AQI: **{round(df_a['AQI'].mean(), 1)}**
    - Unhealthy days: **{unhealthy_a} ({pct_a}%)**
    - Worst single AQI: **{int(df_a['AQI'].max())}**
    """)

with card_b:
    st.markdown(f"#### {city_b}")
    st.markdown(f"""
    - Mean AQI: **{round(df_b['AQI'].mean(), 1)}**
    - Unhealthy days: **{unhealthy_b} ({pct_b}%)**
    - Worst single AQI: **{int(df_b['AQI'].max())}**
    """)
