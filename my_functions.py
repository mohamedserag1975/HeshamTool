import plotly.express as px
import streamlit as st
import pandas as pd
from contextlib import contextmanager
from typing import Generator, Sequence, Any, Dict
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
# from .. import extra

#   Function to generate histogram for UC power-point export
def UC_slide(dataframe, xaxis, yaxis, measure, barmode):
    """
    Creates histogram for the various EBS levels in relation to included duration and count of events
    to make charts ready for capture to the UC slides
    Args:
        dataframe: the dataframe of which the column data is plotted
        xaxis: what series constructs the xaxis
        yaxis: what series constructs the yaxis
        measure: type of the grouping, hours or count
        barmode: Type of the grouping for the histogram bars
    """
    title = "Forced outage " + measure + " " + xaxis
    figname = px.histogram(dataframe, x=xaxis, y=yaxis,
                            color="Rolling Year", barmode=barmode,
                            height=400, title=title,
                            text_auto='.0f')
    figname.update_xaxes(type='category', showgrid=True, ticklabelmode="period", dtick="M1", tickformat="%b\n%Y",
                          categoryorder='total descending', tickfont_size = 20, title_font_size=22)
    figname.update_yaxes(tickfont_size = 20, title = measure, title_font_size=22)
    figname.update_layout(bargap=0.5, title_font_size= 30)
    figname.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    figname.update_layout(legend_title_text="", legend_font_size= 25)
    figname.update_traces(textposition='outside')
    figname.update_layout(uniformtext_minsize=20, uniformtext_mode='hide')
    st.plotly_chart(figname)
    # return figname

#   Function to generate pie chart
def create_pie(dataframe, values, names, title_text):
    pie_name = px.pie(dataframe, values=values, names=names)
    pie_name.update_layout(legend=dict(orientation="v", yanchor="top", y=1, xanchor="right", x=0.1))
    pie_name.update_layout(uniformtext_minsize=20, uniformtext_mode='hide')
    pie_name.update_traces(dict(title_text=title_text,title_position = "top center",
                                      title_font_size= 30))
    pie_name.update_traces(legendgrouptitle_font_size=5)

    return pie_name

#   Function to generate highest hours or counts
def highest_hours(dataframe, target, aggcolumn, aggfunction1, aggfunction2, text1):
    name = dataframe.groupby(target).agg(Hours = (aggcolumn, aggfunction1),
                                         Events = (aggcolumn, aggfunction2))
    name = name.sort_values([text1], ascending=False).head(10).round()

    return name

# Function to generate unique list from a column and add All at the top of the list
def unique(df, col_nme, **kwargs):
    df[col_nme].dropna()
    lst_nme = df[col_nme].unique()
    lst_nme = sorted(list(lst_nme))
    lst_nme.insert(0, "All")

    return lst_nme

#   Main function to read from the Excel sheet data
@st.cache_data
def get_data_from_excel(file):
    # st.cache_resource.clear()
    df = pd.read_excel(file)

    # global pr
    # pr = ProfileReport(df)

    if not df.empty:
        df = df.fillna("NA")
        return df
    else:
        st.write("File contains no data")

#   Cards display function
# @extra
def style_metric_cards(
    background_color: str = "#FFF",
    border_size_px: int = 1,
    border_color: str = "#CCC",
    border_radius_px: int = 5,
    border_left_color: str = "#9AD8E1",
    box_shadow: bool = True,
):

    box_shadow_str = (
        "box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15) !important;"
        if box_shadow
        else "box-shadow: none !important;"
    )
    st.markdown(
        f"""
        <style>
            div[data-testid="metric-container"] {{
                background-color: {background_color};
                border: {border_size_px}px solid {border_color};
                padding: 5% 5% 5% 10%;
                border-radius: {border_radius_px}px;
                border-left: 0.5rem solid {border_left_color} !important;
                {box_shadow_str}
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )

#   Export to CSV Function
@st.cache_data
def _to_csv(data: pd.DataFrame):
    return data.to_csv().encode("utf-8")

_SUPPORTED_EXPORTS = {
    "CSV": {
        "function": _to_csv,
        "extension": ".csv",
        "mime": "text/csv",
    }
}


#   Chart container function
_SUPPORTED_EXPORT_KEYS = list(_SUPPORTED_EXPORTS.keys())


# @extra  # type: ignore
@contextmanager
def chart_container(
    data: pd.DataFrame,
    tabs: Sequence[str] = (
        "Chart 📈",
        "Dataframe 📄",
        "Export 📁",
    ),
    export_formats: Sequence[str] = _SUPPORTED_EXPORT_KEYS,
) -> Generator:
    """Embed chart in a (chart, data, export, explore) tabs container to let the viewer explore and export its underlying data.

    Args:
        data (pd.DataFrame): Dataframe used in the dataframe tab.
        tabs (Sequence, optional): Tab labels. Defaults to ("Chart 📈", "Dataframe 📄", "Export 📁").
        export_formats (Sequence, optional): Export file formats. Defaults to ("CSV", "Parquet")
    """

    assert all(
        export_format in _SUPPORTED_EXPORTS for export_format in export_formats
    ), f"Input format is not supported, please use one within {_SUPPORTED_EXPORTS.keys()}"

    if "chart_container_widget_key" not in st.session_state:
        st.session_state["chart_container_widget_key"] = 0

    def _get_random_widget_key() -> str:
        st.session_state.chart_container_widget_key += 1
        return st.session_state.chart_container_widget_key

    tab_1, tab_2, tab_3 = st.tabs(tabs)

    with tab_1:
        yield

    with tab_2:
        st.dataframe(data, use_container_width=True)

    with tab_3:
        st.caption("Export limited to 1 million rows.")
        export_data = data.head(1_000_000)
        for chosen_export_format in export_formats:
            export_utils = _SUPPORTED_EXPORTS[chosen_export_format]
            exporter = export_utils["function"]
            extension = export_utils["extension"]
            st.download_button(
                f"Download data as {extension}",
                data=exporter(export_data),
                file_name="Customer Events" + extension,
                mime=export_utils.get("mime"),
                key=_get_random_widget_key(),
            )

#   Dataframe explorer function to display filters for the dataframe or the chart
def dataframe_explorer(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns
    Args:
        df (pd.DataFrame): Original dataframe
    Returns:
        pd.DataFrame: Filtered dataframe
    """

    random_key_base = pd.util.hash_pandas_object(df)

    df = df.copy()

    # Try to convert datetimes into standard format (datetime, no timezone)
    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass

        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    modification_container = st.container()

    with modification_container:
        to_filter_columns = st.multiselect(
            "Filter dataframe on",
            df.columns,
            key=f"{random_key_base}_multiselect",
        )
        filters: Dict[str, Any] = dict()
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            # Treat columns with < 10 unique values as categorical
            if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                left.write("↳")
                filters[column] = right.multiselect(
                    f"Values for {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                    key=f"{random_key_base}_{column}",
                )
                df = df[df[column].isin(filters[column])]
            elif is_numeric_dtype(df[column]):
                left.write("↳")
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                filters[column] = right.slider(
                    f"Values for {column}",
                    _min,
                    _max,
                    (_min, _max),
                    step=step,
                    key=f"{random_key_base}_{column}",
                )
                df = df[df[column].between(*filters[column])]
            elif is_datetime64_any_dtype(df[column]):
                left.write("↳")
                filters[column] = right.date_input(
                    f"Values for {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                    key=f"{random_key_base}_{column}",
                )
                if len(filters[column]) == 2:
                    filters[column] = tuple(map(pd.to_datetime, filters[column]))
                    start_date, end_date = filters[column]
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                left.write("↳")
                filters[column] = right.text_input(
                    f"Pattern in {column}",
                    key=f"{random_key_base}_{column}",
                )
                if filters[column]:
                    df = df[df[column].str.contains(filters[column])]

    return df
