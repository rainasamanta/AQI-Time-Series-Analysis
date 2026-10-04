import streamlit as st
import pandas as pd
import plotly.express as px

# Load results from notebook 02
diwali_summary = pd.read_csv("results/diwali_summary.csv")
city_summary_all = pd.read_csv("results/diwali_city_summary.csv")

st.title("Diwali Air Quality Impact")
st.markdown("Is air quality worse during Diwali than in the days around it?")

st.info(
    "**Method:** for each year, the average AQI over the 5 days around Diwali is compared with "
    "the average of the 7 days before and the 7 days after.  \n"
    "**Impact = festival AQI − average of the surrounding weeks.** "
    "Using both weeks cancels out most of the normal seasonal rise in October–November."
)

st.divider()

# City selector
cities = sorted(diwali_summary["City"].unique())
selected_city = st.selectbox("Select a City", cities)

city_years = diwali_summary[diwali_summary["City"] == selected_city].copy()
city_info = city_summary_all[city_summary_all["City"] == selected_city].iloc[0]

years_positive = int(city_info["Years_Positive"])
total_years = len(city_years)
avg_impact = city_info["Avg_Impact"]
avg_impact_pct = city_info["Avg_Impact_Pct"]

st.divider()

# Verdict: is the rise consistent across years?
st.subheader("Verdict")

summary_line = (
    f"Festival AQI was higher than the surrounding weeks in **{years_positive} of {total_years} years**. "
    f"Average impact: **{avg_impact:+.1f} AQI points ({avg_impact_pct:+.1f}%)**."
)

if years_positive >= total_years - 1:
    st.error(f"**Consistent Diwali rise in {selected_city}**  \n{summary_line}")
elif years_positive > total_years / 2:
    st.warning(f"**Diwali rise in most years in {selected_city}, but not all**  \n{summary_line}")
else:
    st.info(f"**No consistent Diwali effect in {selected_city}**  \n{summary_line}")

st.caption(
    "This shows an association, not proof that Diwali caused the change. "
    "Weather and smog episodes can move AQI as much as the festival."
)

st.divider()

# Before / During / After grouped bar chart
st.subheader("Before, During and After Diwali by Year")
st.caption(
    "Average AQI in the 7 days before Diwali, the 5 festival days, and the 7 days after."
)

city_melt = city_years.melt(
    id_vars=["City", "Diwali_Year"],
    value_vars=["Before", "During", "After"],
    var_name="Period",
    value_name="AQI"
)

fig_grouped = px.bar(
    city_melt,
    x="Diwali_Year",
    y="AQI",
    color="Period",
    barmode="group",
    title=f"{selected_city} - AQI Around Diwali by Year",
    color_discrete_map={
        "Before": "#4C9BE8",
        "During": "#E8524C",
        "After": "#F0A500"
    },
    category_orders={"Period": ["Before", "During", "After"]}
)

# Mark 2020 as an unusual year
max_2020 = city_years.loc[city_years["Diwali_Year"] == 2020, ["Before", "During", "After"]].max().max()
fig_grouped.add_annotation(
    x=2020,
    y=max_2020 + 15,
    text="2020: unusual year",
    showarrow=False,
    font=dict(size=11, color="gray")
)

fig_grouped.update_layout(
    xaxis=dict(tickmode="linear"),
    xaxis_title="Year",
    yaxis_title="Mean AQI",
    legend_title="Period",
    hovermode="x unified"
)
st.plotly_chart(fig_grouped, use_container_width=True)

st.divider()

# Impact by year
st.subheader("Diwali Impact by Year")
st.caption(
    "Above zero: festival AQI was higher than the surrounding weeks. "
    "Below zero: it was lower."
)

city_years["Direction"] = city_years["Impact"].apply(
    lambda x: "Higher than surrounding weeks" if x > 0 else "Lower than surrounding weeks"
)

fig_impact = px.bar(
    city_years,
    x="Diwali_Year",
    y="Impact",
    color="Direction",
    color_discrete_map={
        "Higher than surrounding weeks": "#E8524C",
        "Lower than surrounding weeks": "#00B050"
    },
    title=f"{selected_city} - Diwali Impact (Festival AQI − Surrounding Weeks)",
)

fig_impact.add_hline(y=0, line_dash="dash", line_color="black", line_width=1)

fig_impact.update_layout(
    xaxis=dict(tickmode="linear"),
    xaxis_title="Year",
    yaxis_title="Impact (AQI points)",
    legend_title=""
)
st.plotly_chart(fig_impact, use_container_width=True)

st.divider()

# Summary
st.subheader("Diwali Insight")

worst = city_years.loc[city_years["Impact"].idxmax()]
avg_excl_2020 = city_info["Avg_Impact_Excl_2020"]

st.markdown(f"""
- Average impact, all years: **{avg_impact:+.1f} AQI points**
- Average impact, excluding 2020: **{avg_excl_2020:+.1f} AQI points**
- Years with a rise: **{years_positive} of {total_years}**
- Largest rise: **{int(worst['Diwali_Year'])}** ({worst['Impact']:+.1f} AQI points)
""")

st.caption(
    "2020 is shown separately because the pandemic and firecracker restrictions made it an unusual year."
)
