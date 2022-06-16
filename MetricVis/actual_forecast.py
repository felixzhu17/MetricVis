from typing import Optional

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from MetricVis.utils import *


def plot_actual_forecast(
    df: pd.DataFrame,
    actual_col: str,
    forecast_col: str,
    lookback: int = 12,
    metric_name: Optional[str] = None,
):
    return ActualForecast(
        df=df,
        actual_col=actual_col,
        forecast_col=forecast_col,
        lookback=lookback,
        metric_name=metric_name,
    ).create_plot()


class ActualForecast:
    def __init__(
        self,
        df: pd.DataFrame,
        actual_col: str,
        forecast_col: str,
        lookback: int = 12,
        metric_name: Optional[str] = None,
        percentage: bool = False,
        plot_title: Optional[bool] = None,
    ):
        self.df = df[[actual_col, forecast_col]]
        self.actual_col = actual_col
        self.forecast_col = forecast_col
        self.lookback = lookback
        self.metric_name = ifnone(metric_name, clean_text(self.actual_col))
        self.metric_name_py = self.metric_name + " PY"
        self.plot_title = ifnone(plot_title, "Actual vs Forecast - " + self.metric_name)
        self.number_format = format_percentage if percentage else format_absolute
        self.forecast_name = self.metric_name + " Forecast"
        self.plot_df = self._create_monthly_df(self.df)

    def _create_monthly_df(self, df):
        plot_df = df.resample("1M").last()
        plot_df["month"] = plot_df.index.month
        plot_df["year"] = plot_df.index.year
        plot_df.rename(
            {self.actual_col: self.metric_name, self.forecast_col: self.forecast_name},
            axis=1,
            inplace=True,
        )
        plot_df_sample = plot_df.dropna().iloc[-self.lookback :]
        plot_df_sample = plot_df_sample.drop(self.forecast_name, axis=1)
        plot_df_sample[self.metric_name_py] = plot_df_sample.apply(
            get_month_before, axis=1, df=plot_df, col=self.metric_name
        )
        plot_df_sample["YOY Growth"] = (
            plot_df_sample[self.metric_name] / plot_df_sample[self.metric_name_py] - 1
        )
        final_plot_df = (
            plot_df[[self.forecast_name]]
            .loc[plot_df_sample.index[0] :]
            .merge(plot_df_sample, how="left", left_index=True, right_index=True)
        )
        return final_plot_df

    def create_plot(self):
        fig = make_subplots(
            specs=[[{"secondary_y": True}]],
        )

        fig.add_trace(
            go.Scatter(
                x=self.plot_df.index,
                y=self.plot_df[self.metric_name],
                name=self.metric_name,
                legendgroup=self.metric_name,
                line=dict(color="#0052CC"),
                showlegend=True,
                mode="lines+markers+text",
                text=self.plot_df[self.metric_name].apply(self.number_format),
                textposition="top center",
                cliponaxis=False,
            ),
            secondary_y=True,
        )

        fig.add_trace(
            go.Scatter(
                x=self.plot_df.index,
                y=self.plot_df[self.forecast_name],
                name=self.forecast_name,
                legendgroup=self.forecast_name,
                line=dict(color="#00B8D9"),
                showlegend=True,
                mode="lines",
            ),
            secondary_y=True,
        )

        fig.add_trace(
            go.Scatter(
                x=self.plot_df.index,
                y=self.plot_df["YOY Growth"],
                name="YOY Growth",
                legendgroup="YOY Growth",
                line=dict(color="#C1C7D0", dash="dash"),
                showlegend=True,
                mode="lines",
            )
        )

        fig.add_trace(
            go.Scatter(
                x=self.plot_df.index,
                y=self.plot_df[self.metric_name_py],
                name=self.metric_name_py,
                legendgroup=self.metric_name_py,
                line=dict(color="#C1C7D0"),
                showlegend=True,
                mode="lines",
            ),
            secondary_y=True,
        )

        fig.update_yaxes(range=[0, 1], secondary_y=False)

        fig.update_layout(
            legend=dict(
                orientation="h", xanchor="center", yanchor="bottom", x=0.5, y=-0.5
            ),
            legend_title_text="",
            plot_bgcolor="white",
            title=self.plot_title,
        )

        fig.update_layout(
            dict(
                yaxis2={"anchor": "x", "overlaying": "y", "side": "left"},
                yaxis={"anchor": "x", "domain": [0.0, 1.0], "side": "right"},
                yaxis_tickformat=".0%",
            )
        )

        return fig
