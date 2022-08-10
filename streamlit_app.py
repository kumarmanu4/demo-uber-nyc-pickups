# -*- coding: utf-8 -*-
# Copyright 2018-2022 Streamlit Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""An example of showing geographic data."""

import altair as alt
import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st
from ipywidgets import HTML

# SETTING PAGE CONFIG TO WIDE MODE AND ADDING A TITLE AND FAVICON
st.set_page_config(layout="wide", page_title="NYC Ridesharing Demo", page_icon=":taxi:")

# LOAD DATA ONCE
@st.experimental_singleton
def load_data():
    data = pd.read_csv(
        "IndianSoilData.csv",
        nrows=100000,  # approx. 10% of data
        names=[
            "year",
            "city",
            "state",
            "lat",
            "lon",
            "N",
            "P",
            "K"
        ],  # specify names directly since they don't change
        skiprows=1,  # don't read header since names specified directly
        usecols=[0, 1, 2, 3, 4, 5, 6, 7],  
        
    )

    return data

COLOR_BREWER_BLUE_SCALE = [
    [240, 249, 232],
    [204, 235, 197],
    [168, 221, 181],
    [123, 204, 196],
    [67, 162, 202],
    [8, 104, 172],
]

color_range2 = [ [65, 182, 196],
    [254, 178, 76],
    [253, 141, 60],
    [252, 78, 42],
    [227, 26, 28],
    [189, 0, 38]]

# FUNCTION FOR AIRPORT MAPS
def map(data, lat, lon, zoom):
    st.write(
        pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v9",
            initial_view_state={
                "latitude": lat,
                "longitude": lon,
                "zoom": zoom,
                "pitch": 0,
            },
            layers=[
                pdk.Layer(
    "HeatmapLayer",
    data=data,
    opacity=0.9,
    get_position=["lon", "lat"],
    aggregation=pdk.types.String("MEAN"),
    color_range=COLOR_BREWER_BLUE_SCALE,
    threshold=1,
    get_weight="N",
    pickable=True,
),
                pdk.Layer(
    "HeatmapLayer",
    data=data,
    opacity=0.9,
    get_position=["lon", "lat"],
    threshold=1,
    aggregation=pdk.types.String("MEAN"),
    color_range=color_range2,
    get_weight="P",
    pickable=True,
),
                pdk.Layer(
    "HeatmapLayer",
    data=data,
    opacity=0.9,
    get_position=["lon", "lat"],
    threshold=1,
    aggregation=pdk.types.String("MEAN"),
    get_weight="K",
    pickable=True,
),
                
            ],
        )
    )

# STREAMLIT APP LAYOUT
data = load_data()    
    
text = HTML(value='Move the viewport')
layer = pdk.Layer(
    'ScatterplotLayer',
    data=data,
    pickable=True,
    get_position=['lon', 'lat'],
    get_fill_color=[255, 0, 0],
    get_radius=100
)
r = pdk.Deck(layer)

def filter_by_bbox(row, west_lng, east_lng, north_lat, south_lat):
    return west_lng < row['lon'] < east_lng and south_lat < row['lat'] < north_lat

def filter_by_viewport(widget_instance, payload):
    try:
        west_lng, north_lat = payload['data']['nw']
        east_lng, south_lat = payload['data']['se']
        filtered_df = df[df.apply(lambda row: filter_by_bbox(row, west_lng, east_lng, north_lat, south_lat), axis=1)]
        text.value = 'Points in viewport: %s' % int(filtered_df.count()['lon'])
    except Exception as e:
        text.value = 'Error: %s' % e


r.deck_widget.on_click(filter_by_viewport)
#display(text)
r.show()    

# FILTER DATA FOR A SPECIFIC HOUR, CACHE
@st.experimental_memo
def filterdata(df, year_selected):
    return df[df["year"] == year_selected]


# CALCULATE MIDPOINT FOR GIVEN SET OF DATA
@st.experimental_memo
def mpoint(lat, lon):
    return (np.average(lat), np.average(lon))


# FILTER DATA BY HOUR
@st.experimental_memo
def histdata(df, hr):
    filtered = data[
        (df["date/time"].dt.hour >= hr) & (df["date/time"].dt.hour < (hr + 1))
    ]

    hist = np.histogram(filtered["date/time"].dt.minute, bins=60, range=(0, 60))[0]

    return pd.DataFrame({"minute": range(60), "pickups": hist})




# LAYING OUT THE TOP SECTION OF THE APP
row1_1, row1_2 = st.columns((2, 3))

# SEE IF THERE'S A QUERY PARAM IN THE URL (e.g. ?pickup_hour=2)
# THIS ALLOWS YOU TO PASS A STATEFUL URL TO SOMEONE WITH A SPECIFIC HOUR SELECTED,
# E.G. https://share.streamlit.io/streamlit/demo-uber-nyc-pickups/main?pickup_hour=2
if not st.session_state.get("url_synced", False):
    try:
        year = int(st.experimental_get_query_params()["year"][0])
        st.session_state["year"] = year
        st.session_state["url_synced"] = True
    except KeyError:
        pass

# IF THE SLIDER CHANGES, UPDATE THE QUERY PARAM
def update_query_params():
    year_selected = st.session_state["year"]
    st.experimental_set_query_params(year=year_selected)


with row1_1:
    st.title("Indian Soil Data")
    hour_selected = st.slider(
        "Select Year", 1990, 2022, key="year", on_change=update_query_params
    )


with row1_2:
    st.write(
        """
    ##
    Examining how Uber pickups vary over time in New York City's and at its major regional airports.
    By sliding the slider on the left you can view different slices of time and explore different transportation trends.
    """
    )

# LAYING OUT THE MIDDLE SECTION OF THE APP WITH THE MAPS
row2_1, row2_2, row2_3, row2_4 = st.columns((2, 1, 1, 1))

# SETTING THE ZOOM LOCATIONS FOR THE AIRPORTS
la_guardia = [40.7900, -73.8700]
jfk = [40.6650, -73.7821]
newark = [40.7090, -74.1805]
zoom_level = 12
midpoint = mpoint(data["lat"], data["lon"])

with row2_1:
    st.write(
        f"""**indian cities map**"""
    )
    map(filterdata(data, year_selected), midpoint[0], midpoint[1], 11)
