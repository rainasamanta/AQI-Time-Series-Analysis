import streamlit as st

st.set_page_config(
    page_title="AQI Health Exposure Tracker",
    page_icon="🌫️",
    layout="wide"
)

st.title("AQI Health Exposure Tracker")
st.markdown("### Quantifying the human cost of urban air pollution")

st.divider()

st.markdown("""
This app analyses air quality data across four Indian cities -
**Bengaluru, Delhi, Kolkata, and Mumbai** - from January 2019 to March 2025.
""")

st.divider()

st.markdown("""
| Page | What it answers |
|---|---|
| City Overview | What does AQI look like in my city over time? |
| City Comparison | Which city has a worse health burden? |
| Seasonal Patterns | Which months are safest and most dangerous? |
| Diwali Impact | Does Diwali significantly worsen air quality? |
| SARIMA Forecast | How accurately can we predict future AQI? |
""")

st.divider()

st.caption(
    "Data source: Central Pollution Control Board (CPCB), India. "
    "Analysis by Raina Samanta."
)