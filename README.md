# AQI Forecasting and Diwali Impact Analysis
### An end-to-end time series analysis of Air Quality Index (AQI) data across 4 Indian cities, featuring exploratory analysis, a Diwali impact study, SARIMA forecasting benchmarked against simple baselines, and an interactive Streamlit dashboard.

## Cities and Study Period
Bengaluru | Delhi | Kolkata | Mumbai    January 2019 - March 2025 (daily CPCB AQI data)

## Objectives
- Explore AQI patterns across cities
- Measure how AQI changes around Diwali
- Investigate seasonality and trends
- Build SARIMA forecasting models
- Test whether SARIMA beats simple seasonal baselines

## Dashboard
[Live Streamlit App](https://aqi-time-series-analysis.streamlit.app/)

## Analysis Pipeline
1. **Data cleaning and EDA:** date parsing, duplicate and missing-date checks, CPCB AQI categories, distribution and seasonal plots
2. **Diwali impact study:** festival-period AQI (5 days) compared with the average of the week before and the week after, so the normal seasonal rise cancels out
3. **Model selection:** STL decomposition, ADF and KPSS tests, OCSB and Canova-Hansen seasonal tests, AIC grid search; the model constraint setting chosen on a 2023 validation year
4. **Forecasting:** 15-month forecast (Jan 2024 - Mar 2025) compared with two baselines (same month last year, and each month's 2019-2023 average), plus Ljung-Box residual checks

## SARIMA Forecasting
Models were trained on monthly AQI from January 2019 to December 2023 and used to forecast January 2024 to March 2025 (15 months) in one run, without seeing any test data.

| City | Model | Constrained |
|---|---|---|
| Bengaluru | SARIMA(1,0,1)(1,0,1,12) | Yes |
| Delhi | SARIMA(1,1,1)(1,1,0,12) | No |
| Kolkata | SARIMA(1,1,1)(1,0,1,12) | Yes |
| Mumbai | SARIMA(0,1,1)(1,0,1,12) | Yes |

## Forecast Performance
SARIMA compared with two simple baselines on the same test period (lower MAE is better; best per city in bold).

| City | SARIMA MAE | SARIMA R² | Last Year MAE | Last Year R² | Monthly Avg MAE | Monthly Avg R² |
|---|---|---|---|---|---|---|
| Bengaluru | 5.14 | 0.866 | 8.65 | 0.625 | **4.36** | **0.898** |
| Delhi | 24.43 | 0.895 | 22.38 | 0.880 | **21.87** | **0.904** |
| Kolkata | 57.93 | -0.332 | **12.05** | **0.887** | 29.85 | 0.444 |
| Mumbai | **14.98** | **0.743** | 38.22 | -0.610 | 24.10 | 0.299 |

- **Last Year:** each month forecast as the same month in 2023
- **Monthly Avg:** each month forecast as its 2019–2023 average

## Key Findings
- Delhi had unhealthy air (AQI above 200) on 46.6% of days, compared with 0% in Bengaluru
- No city showed a consistent Diwali effect: festival AQI rose in 3-4 of 6 years per city, with Mumbai most consistent (4 of 6 years, +9.2 AQI on average)
- SARIMA beat both baselines only for Mumbai, with 38% lower error (MAE 14.98 vs 24.10, R² = 0.743)
- For Bengaluru and Delhi, a simple monthly-average baseline matched or slightly beat SARIMA (R² 0.898 vs 0.866 and 0.904 vs 0.895), showing that most of the pattern is the yearly cycle
- Kolkata's SARIMA forecast drifted too low (R² = -0.33); the same-month-last-year baseline performed best (R² = 0.887)
- Mumbai's January-March AQI fell 38% from 2023 to 2024 (181 to 112), a level shift that makes early 2024 hard to forecast
**Notebooks** (run in order: 01 → 02 → 03 → 04)
```bash
pip install -r requirements.txt
pip install jupyter matplotlib seaborn scikit-learn pmdarima
jupyter notebook
```
