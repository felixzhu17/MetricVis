# MetricVis
https://www.holistics.io/blog/how-amazon-measures/

## Installing
```
pip install metric-vis
``` 

## Quickstart

``` python
from MetricVis import plot_week_month_trend
import pandas as pd
monthly_df = pd.read_csv('demo_data/monthly_data.csv')
monthly_df.index = pd.to_datetime(monthly_df.Day)
weekly_df = pd.read_csv('demo_data/weekly_data.csv')
weekly_df.index = pd.to_datetime(weekly_df.Day)
plot_week_month_trend(weekly_df = weekly_df, monthly_df = monthly_df, col_name = "Metric", month_lookback = 11)
```
<img alt="Weekly/Monthly Trend" src="images/weekly_monthly_trend.png">

``` python
from MetricVis import plot_actual_forecast
import pandas as pd
forecast_df = pd.read_csv('demo_data/forecast_data.csv')
forecast_df.index = pd.to_datetime(forecast_df.Day)
plot_actual_forecast(df = forecast_df, actual_col = "Metric", forecast_col = "Forecast", lookback = 8)
```
<img alt="Actual vs Forecast" src="images/actual_vs_forecast.png">