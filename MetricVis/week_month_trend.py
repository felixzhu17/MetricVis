from typing import Optional

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from MetricVis.utils import *


def plot_week_month_trend(
    weekly_df: pd.DataFrame,
    monthly_df: pd.DataFrame,
    col_name: str,
    week_lookback: int = 6,
    month_lookback: int = 12,
    week_relative_width: float = 0.25,
    metric_name: Optional[str] = None,
    percentage: bool = False,
    different_axis: bool = True,
    plot_title: Optional[bool] = None,
):
    return WeekMonthTrend(
        weekly_df=weekly_df,
        monthly_df=monthly_df,
        col_name=col_name,
        week_lookback=week_lookback,
        month_lookback=month_lookback,
        week_relative_width=week_relative_width,
        metric_name=metric_name,
        percentage=percentage,
        different_axis=different_axis,
        plot_title=plot_title,
    ).create_plot()


class WeekMonthTrend:
    def __init__(
        self,
        weekly_df: pd.DataFrame,
        monthly_df: pd.DataFrame,
        col_name: str,
        week_lookback: int = 6,
        month_lookback: int = 12,
        week_relative_width: float = 0.25,
        metric_name: Optional[str] = None,
        percentage: bool = False,
        different_axis: bool = True,
        plot_title: bool = None,
    ):

        self.col_name = col_name
        self.week_lookback = week_lookback
        self.month_lookback = month_lookback
        self.week_relative_width = week_relative_width
        self.different_axis = different_axis
        self.metric_name = ifnone(metric_name, clean_text(self.col_name))
        self.metric_name_py = self.metric_name + " PY"
        self.plot_title = ifnone(
            plot_title, "Weekly/Monthly Trend - " + self.metric_name
        )
        self.number_format = format_percentage if percentage else format_absolute
        self.weekly_df = self._create_weekly_df(weekly_df)
        self.monthly_df = self._create_monthly_df(monthly_df)

    def _create_weekly_df(self, weekly_df):
        weekly_df = weekly_df.sort_index()
        weekly_df = weekly_df[[self.col_name]].resample("1W").last()
        weekly_df.rename({self.col_name: self.metric_name}, axis=1, inplace=True)
        weekly_df["week"] = weekly_df.index.isocalendar().week
        weekly_df["year"] = weekly_df.index.year
        weekly_df_sample = weekly_df.iloc[-self.week_lookback :]
        weekly_df_sample[self.metric_name_py] = weekly_df_sample.apply(
            get_week_before, axis=1, df=weekly_df, col=self.metric_name
        )
        weekly_df_sample.index = weekly_df_sample.index.strftime("Wk%W '%y")
        return weekly_df_sample

    def _create_monthly_df(self, monthly_df):
        monthly_df = monthly_df.sort_index()
        monthly_df = monthly_df[[self.col_name]].resample("1M").last()
        monthly_df.rename({self.col_name: self.metric_name}, axis=1, inplace=True)
        monthly_df["month"] = monthly_df.index.month
        monthly_df["year"] = monthly_df.index.year
        monthly_df_sample = monthly_df.iloc[-self.month_lookback :]
        monthly_df_sample[self.metric_name_py] = monthly_df_sample.apply(
            get_month_before, axis=1, df=monthly_df, col=self.metric_name
        )
        monthly_df_sample.index = monthly_df_sample.index.strftime("%b '%y")
        return monthly_df_sample

    def create_plot(self):
        fig = make_subplots(
            rows=1,
            cols=2,
            column_widths=[self.week_relative_width, 1 - self.week_relative_width],
            horizontal_spacing=0.025,
            specs=[
                [
                    {"secondary_y": self.different_axis},
                    {"secondary_y": self.different_axis},
                ]
            ],
        )
        fig.add_trace(
            go.Scatter(
                x=self.weekly_df.index,
                y=self.weekly_df[self.metric_name],
                name=self.metric_name,
                legendgroup=self.metric_name,
                line=dict(color="#0052CC"),
                showlegend=True,
                mode="lines+markers+text",
                text=self.weekly_df[self.metric_name].apply(self.number_format),
                textposition="top center",
                cliponaxis=False,
            ),
            row=1,
            col=1,
        )

        fig.add_trace(
            go.Scatter(
                x=self.weekly_df.index,
                y=self.weekly_df[self.metric_name_py],
                name=self.metric_name_py,
                legendgroup=self.metric_name_py,
                line=dict(color="#C1C7D0"),
                showlegend=True,
                mode="lines",
            ),
            row=1,
            col=1,
        )

        fig.add_trace(
            go.Scatter(
                x=self.monthly_df.index,
                y=self.monthly_df[self.metric_name],
                name=self.metric_name,
                legendgroup=self.metric_name,
                line=dict(color="#0052CC"),
                mode="lines+markers+text",
                text=self.monthly_df[self.metric_name].apply(self.number_format),
                textposition="top center",
                showlegend=False,
                cliponaxis=False,
            ),
            secondary_y=self.different_axis,
            row=1,
            col=2,
        )

        fig.add_trace(
            go.Scatter(
                x=self.monthly_df.index,
                y=self.monthly_df[self.metric_name_py],
                name=self.metric_name_py,
                legendgroup=self.metric_name_py,
                line=dict(color="#C1C7D0"),
                showlegend=False,
                mode="lines",
            ),
            secondary_y=self.different_axis,
            row=1,
            col=2,
        )

        if self.different_axis is False:
            fig.update_yaxes(range=self._get_min_max())
            fig.update_yaxes(showticklabels=False, row=1, col=2)

        fig.update_layout(
            legend=dict(
                orientation="h", xanchor="center", yanchor="bottom", x=0.5, y=-0.5
            ),
            legend_title_text="",
            plot_bgcolor="white",
            title=self.plot_title,
        )
        return fig

    def _get_min_max(self, buffer=0.2):
        minimum = min(
            self.weekly_df[self.metric_name].min(),
            self.weekly_df[self.metric_name_py].min(),
            self.monthly_df[self.metric_name].min(),
            self.monthly_df[self.metric_name_py].min(),
        )
        maximum = max(
            self.weekly_df[self.metric_name].max(),
            self.weekly_df[self.metric_name_py].max(),
            self.monthly_df[self.metric_name].max(),
            self.monthly_df[self.metric_name_py].max(),
        )
        return [minimum * (1 - buffer), maximum * (1 + buffer)]
