import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from statsmodels.tsa.statespace.sarimax import SARIMAX
import warnings
warnings.filterwarnings("ignore")

# Load data (dates are stored as YYYY-MM-DD)
df = pd.read_csv("data/aqi_master_clean.csv")
df['Date'] = pd.to_datetime(df['Date'])

# Results from notebooks 03 and 04
best_models = pd.read_csv("results/best_sarima_models.csv")
comparison = pd.read_csv("results/forecast_comparison.csv")
ljungbox = pd.read_csv("results/ljungbox_results.csv")

# Monthly average AQI per city
monthly_df = (
    df.groupby(['City', pd.Grouper(key='Date', freq='MS')])['AQI']
    .mean()
    .reset_index()
)

# City notes
notes = {
    'Mumbai': (
        "Mumbai's winter AQI dropped sharply in 2024: the January–March average fell from about "
        "181 in 2023 to about 112 in 2024. Any model trained on 2019–2023 expects a dirtier winter, "
        "so early 2024 is harder to forecast. Even so, "
        "SARIMA beat both simple baselines for Mumbai."
    ),
    'Kolkata': (
        "The Kolkata model gets the seasonal shape right but drifts too low, even below zero, which "
        "is impossible for AQI. Because the model forecasts month-to-month changes (d = 1), an error "
        "in the first month carries through the whole forecast. The simple last-year baseline "
        "performed best for Kolkata."
    ),
}

st.title("SARIMA Forecast")
st.markdown("How well does the model predict 2024–25 air quality, and does it beat simple guesses?")

st.divider()

# City selector
cities = sorted(best_models['City'])
selected_city = st.selectbox("Select a City", cities)

row = best_models[best_models['City'] == selected_city].iloc[0]
order = (int(row['p']), int(row['d']), int(row['q']))
seasonal_order = (int(row['P']), int(row['D']), int(row['Q']), 12)
enforce = str(row['Enforce']) == 'True'

# Train / test split
series = monthly_df[monthly_df['City'] == selected_city].set_index('Date')['AQI']
series.index.freq = 'MS'
train = series[:'2023-12-31']
test = series['2024-01-01':]

# Fit SARIMA
model = SARIMAX(
    train,
    order=order,
    seasonal_order=seasonal_order,
    enforce_stationarity=enforce,
    enforce_invertibility=enforce
)

with st.spinner("Fitting SARIMA model..."):
    fitted = model.fit(disp=False)

forecast = fitted.get_forecast(steps=len(test))
pred = forecast.predicted_mean
conf_int = forecast.conf_int()

# Baselines (same as notebook 04)
last_year_pred = np.tile(train.iloc[-12:].values, 2)[:len(test)]
month_means = train.groupby(train.index.month).mean()
monthly_avg_pred = test.index.month.map(month_means).values

st.divider()

# Forecast plot
st.subheader(f"{selected_city} - Forecast vs Actual")
st.caption(
    "Trained on 2019–2023 data. The shaded region is the 95% confidence interval. "
    "Dashed and dotted lines are the two simple baselines."
)

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=train.index, y=train.values,
    name="Training Data",
    line=dict(color="#4C9BE8", width=1.5)
))

fig.add_trace(go.Scatter(
    x=test.index, y=test.values,
    name="Actual",
    line=dict(color="black", width=2)
))

fig.add_trace(go.Scatter(
    x=pred.index, y=pred.values,
    name="SARIMA",
    line=dict(color="#E8524C", width=2)
))

fig.add_trace(go.Scatter(
    x=list(conf_int.index) + list(conf_int.index[::-1]),
    y=list(conf_int.iloc[:, 0]) + list(conf_int.iloc[:, 1][::-1]),
    fill="toself",
    fillcolor="rgba(232, 82, 76, 0.15)",
    line=dict(color="rgba(255,255,255,0)"),
    name="95% Confidence Interval"
))

fig.add_trace(go.Scatter(
    x=test.index, y=last_year_pred,
    name="Last year",
    line=dict(color="#00B050", width=1.5, dash="dash")
))

fig.add_trace(go.Scatter(
    x=test.index, y=monthly_avg_pred,
    name="Monthly average",
    line=dict(color="#9467BD", width=1.5, dash="dot")
))

fig.add_vline(
    x=pd.Timestamp("2024-01-01").timestamp() * 1000,
    line_dash="dot",
    line_color="gray",
    annotation_text="Forecast start",
    annotation_position="top right"
)

fig.update_layout(
    xaxis_title="Date",
    yaxis_title="Monthly Mean AQI",
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# Metrics
st.subheader("SARIMA Accuracy")

city_comp = comparison[comparison['City'] == selected_city]
sarima = city_comp[city_comp['Model'] == 'SARIMA'].iloc[0]

m1, m2, m3, m4 = st.columns(4)
m1.metric("MAE", f"{sarima['MAE']}")
m2.metric("RMSE", f"{sarima['RMSE']}")
m3.metric("MAPE", f"{sarima['MAPE']}%")
m4.metric("R²", f"{sarima['R2']}")

st.divider()

# SARIMA vs baselines
st.subheader("Does SARIMA Beat Simple Guesses?")
st.caption(
    "Last year: each month = the same month in 2023. "
    "Monthly average: each month = its average over 2019–2023."
)

st.dataframe(
    city_comp[['Model', 'MAE', 'RMSE', 'MAPE', 'R2']].reset_index(drop=True),
    hide_index=True,
    use_container_width=True
)

baselines = city_comp[city_comp['Model'] != 'SARIMA']
best_baseline = baselines.loc[baselines['MAE'].idxmin()]
improvement = (best_baseline['MAE'] - sarima['MAE']) / best_baseline['MAE'] * 100

if sarima['MAE'] < best_baseline['MAE']:
    st.success(
        f"SARIMA beat the best simple baseline (**{best_baseline['Model']}**), "
        f"with **{improvement:.0f}% lower** average error."
    )
else:
    st.warning(
        f"The simple **{best_baseline['Model']}** baseline did better than SARIMA "
        f"(MAE {best_baseline['MAE']} vs {sarima['MAE']}). "
        f"Most of {selected_city}'s pattern is the regular yearly cycle."
    )

st.divider()

# Plain English interpretation
st.subheader("What do these numbers mean?")

if sarima['R2'] > 0:
    r2_line = f"The model explains **{round(sarima['R2'] * 100, 1)}%** of the variation in {selected_city}'s 2024–25 monthly AQI (R²)"
else:
    r2_line = "R² is negative: the forecast was worse than simply guessing the 2024–25 average every month"

st.markdown(f"""
- The model's monthly forecast was off by **{sarima['MAE']} AQI points** on average (MAE)
- In percentage terms, forecasts were off by **{sarima['MAPE']}%** on average (MAPE)
- {r2_line}
""")

# Residual check
lb = ljungbox[ljungbox['City'] == selected_city].iloc[0]
if lb['P_Value'] > 0.05:
    st.info(
        f"**Residual check (Ljung-Box p = {lb['P_Value']}):** no leftover pattern in the "
        "model's training errors."
    )
else:
    st.warning(
        f"**Residual check (Ljung-Box p = {lb['P_Value']}):** some pattern is left in the "
        "model's training errors, so the confidence band may be too narrow."
    )

# City-specific note
if selected_city in notes:
    st.divider()
    st.subheader("Note")
    st.info(notes[selected_city])

st.divider()

# Model specification
st.subheader("Model Specification")
st.caption(
    "Orders chosen by AIC grid search on 2019–2023. Whether to constrain the model "
    "was chosen by forecasting 2023 from 2019–2022 data."
)

spec_col1, spec_col2, spec_col3 = st.columns(3)

with spec_col1:
    st.markdown(f"""
    **Non-seasonal**
    - p (AR order): **{order[0]}**
    - d (differencing): **{order[1]}**
    - q (MA order): **{order[2]}**
    """)

with spec_col2:
    st.markdown(f"""
    **Seasonal** (period = 12 months)
    - P (seasonal AR): **{seasonal_order[0]}**
    - D (seasonal differencing): **{seasonal_order[1]}**
    - Q (seasonal MA): **{seasonal_order[2]}**
    """)

with spec_col3:
    st.markdown(f"""
    **Constraints**
    - {"Constrained (stable coefficients)" if enforce else "Unconstrained"}
    """)
