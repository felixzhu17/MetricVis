from re import I
from typing import Optional, Union

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from MetricVis.utils import *


def plot_actual_forecast(
    df: pd.DataFrame,
    actual_col: str,
    forecast_col: Union[str, list],
    lookback: int = 12,
    metric_name: Optional[str] = None,
    forecast_name: Optional[Union[str, list]] = None,
    percentage: bool = False,
    plot_title: Optional[bool] = None,
    forecast_color: Optional[Union[str, list]] = None,
    plotsize: Optional[list] = None,
):
    return ActualForecast(
        df=df,
        actual_col=actual_col,
        forecast_col=forecast_col,
        lookback=lookback,
        metric_name=metric_name,
        forecast_name=forecast_name,
        percentage=percentage,
        plot_title=plot_title,
        forecast_color=forecast_color,
        plotsize=plotsize,
    ).create_plot()


class ActualForecast:
    def __init__(
        self,
        df: pd.DataFrame,
        actual_col: str,
        forecast_col: Union[str, list],
        lookback: int = 12,
        metric_name: Optional[str] = None,
        forecast_name: Optional[Union[str, list]] = None,
        percentage: bool = False,
        plot_title: Optional[bool] = None,
        forecast_color: Optional[Union[str, list]] = None,
        plotsize: Optional[list] = None,
    ):

        self.actual_col = actual_col
        self.forecast_col = forecast_col
        self.multi_forecast = check_list_type(self.forecast_col)
        self.df = df[[actual_col] + convert_list_if_not(forecast_col)]
        self.lookback = lookback
        self.metric_name = ifnone(metric_name, clean_text(self.actual_col))
        self.metric_name_py = self.metric_name + " PY"
        self.plot_title = ifnone(plot_title, "Actual vs Forecast - " + self.metric_name)
        self.number_format = format_percentage if percentage else format_absolute
        self.forecast_name = ifnone(
            forecast_name,
            [self.metric_name + f" Forecast {i+1}" for i in range(len(forecast_col))]
            if self.multi_forecast
            else self.metric_name + " Forecast",
        )
        self.plot_df = self._create_monthly_df(self.df)
        self.forecast_color = ifnone(forecast_color, CORE_COLOURS)
        self.plotsize = plotsize

    def _create_monthly_df(self, df):
        plot_df = df.resample("1M").last()
        plot_df["month"] = plot_df.index.month
        plot_df["year"] = plot_df.index.year

        if self.multi_forecast:
            rename_dict = {i: j for i, j in zip(self.forecast_col, self.forecast_name)}
            rename_dict[self.actual_col] = self.metric_name
        else:
            rename_dict = {
                self.actual_col: self.metric_name,
                self.forecast_col: self.forecast_name,
            }

        plot_df.rename(
            rename_dict,
            axis=1,
            inplace=True,
        )
        final_index = np.where(plot_df[self.metric_name].notnull())[0][-1]
        plot_df_sample = plot_df.iloc[final_index - self.lookback + 1 :]
        plot_df_sample = plot_df_sample.drop(self.forecast_name, axis=1)
        plot_df_sample[self.metric_name_py] = plot_df_sample.apply(
            get_month_before, axis=1, df=plot_df, col=self.metric_name
        )
        plot_df_sample["YOY Growth"] = (
            plot_df_sample[self.metric_name] / plot_df_sample[self.metric_name_py] - 1
        )

        final_plot_df = (
            plot_df[convert_list_if_not(self.forecast_name)]
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

        for i, j in zip(convert_list_if_not(self.forecast_name), self.forecast_color):
            fig.add_trace(
                go.Scatter(
                    x=self.plot_df.index,
                    y=self.plot_df[i],
                    name=i,
                    legendgroup=i,
                    line=dict(color=j),
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

        if self.plotsize:
            fig.update_layout(
                width=self.plotsize[0],
                height=self.plotsize[1],
            )

        return fig
