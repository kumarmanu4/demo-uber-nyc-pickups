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
st.set_page_config(layout="wide", page_title="Soil Fertilizer Prediction", page_icon=":factory:")

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
            map_style="mapbox://styles/mapbox/satellite-streets-v11",
            initial_view_state={
                "latitude": lat,
                "longitude": lon,
                "zoom": zoom,
                "pitch": 0,
            },
            layers=[
                layer_selected
                
            ],
            tooltip={
        'html': '<b>Elevation Value:</b> {elevationValue}',
        'style': {
            'color': 'white'
        }
    }
        )
    )

   


# STREAMLIT APP LAYOUT
data = load_data()


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
    st.title("Soil fertilizer prediction")
    year_selected = st.slider(
        "Select Year", 1990, 2022, key="year", on_change=update_query_params
    )

data_filter = filterdata(data, year_selected)    
    
layer1 = pdk.Layer(
    'ScatterplotLayer',     # Change the `type` positional argument here
    data=data_filter,
    get_position=['lon', 'lat'],
    auto_highlight=True,
    get_radius=10000,          # Radius is given in meters
    get_fill_color=[180, 0, 200, 140],  # Set an RGBA value for fill
    pickable=True)

layerN = pdk.Layer(
    "HeatmapLayer",
    data=data_filter,
    opacity=0.9,
    get_position=["lon", "lat"],
    aggregation=pdk.types.String("MEAN"),
    color_range=COLOR_BREWER_BLUE_SCALE,
    threshold=1,
    get_weight="N",
    pickable=True,
)

layerP = pdk.Layer(
    "HeatmapLayer",
    data=data_filter,
    opacity=0.9,
    get_position=["lon", "lat"],
    threshold=1,
    aggregation=pdk.types.String("MEAN"),
    color_range=COLOR_BREWER_BLUE_SCALE,
    get_weight="P",
    pickable=True,
)

layerK = pdk.Layer(
    "HeatmapLayer",
    data=data_filter,
    opacity=0.9,
    get_position=["lon", "lat"],
    threshold=1,
    aggregation=pdk.types.String("MEAN"),
    color_range=COLOR_BREWER_BLUE_SCALE,
    get_weight="K",
    pickable=True,
)
    
layerH = pdk.Layer(
                    "HexagonLayer",
                    data=data,
                    get_position=["lon", "lat"],
                    radius=100,
                    elevation_scale=4,
                    elevation_range=[0, 1000],
                    pickable=True,
                    extruded=True,
                )

Temp = st.number_input('Enter Temperature:')
st.write('The Temperature is: ', Temp)

Humidity = st.number_input('Enter Humidity:')
st.write('The Humidity is: ', Humidity)

RainFall = st.number_input('Enter Rainfall:')
st.write('The RainFall is: ', RainFall)

pH = st.number_input('Enter pH:')
st.write('The pH is: ', pH)

Crop = st.text_input('Enter Crop:')
st.write('The Crop is: ', Crop)

Soil = st.text_input('Enter Soil:')
st.write('The Soil is: ', Soil)


option = st.selectbox(
     'Select the option?',
     ('N', 'P', 'K', 'Scatter'))    
st.write('You selected:', option)

if option == 'N':
    layer_selected=layerN
elif option == 'P':
    layer_selected=layerP
elif option == 'K':
    layer_selected=layerK
else:
    layer_selected=layer1

df = pd.read_csv(
        "Indian_location_soil.csv",
        nrows=100000,  # approx. 10% of data
        names=[
            "Temperature",
            "Humidity",
            "Rainfall",
            "pH",            
            "N",
            "P",
            "K",
            "Soil",
            "Crop",
            "Fertilizer",
            "lat",
            "lon"
        ],  # specify names directly since they don't change
        skiprows=1,  # don't read header since names specified directly
        usecols=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],          
    )    
    
st.vega_lite_chart(df, {
     'mark': {'type': 'circle', 'tooltip': True},
     'encoding': {
         'x': {'field': 'Rainfall', 'type': 'quantitative'},
         'y': {'field': 'Temperature', 'type': 'quantitative'},                 
         'strokeWidth': {'field': 'Humidity', 'type': 'quantitative'},
         'color': {'field': 'Temperature', 'type': 'quantitative'},
         'size': {'field': 'pH', 'type': 'quantitative'},
          "longitude": {'field': 'lon', 'type': 'quantitative'},
    "latitude": {'field': 'lat', 'type': 'quantitative'}
     },
 }, use_container_width=True)    
    
with row1_2:
    st.write(
        """
    ##
    Prediction of correct fertilizer usage, from soil and environmental metrics of a region.
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
        f"""**Indian cities map**"""
    )
    map(data_filter, midpoint[0], midpoint[1], 11)
