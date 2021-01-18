import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import pydeck as pdk

# SETTING PAGE CONFIG TO WIDE MODE
st.set_page_config(layout="wide")

DATE_COLUMN = 'date/time'
DATA_URL = ('https://s3-us-west-2.amazonaws.com/'
         'streamlit-demo-data/uber-raw-data-sep14.csv.gz')
@st.cache
def load_data(nrows):
    data = pd.read_csv(DATA_URL,nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    return data

# Load 10,000 rows of data into the dataframe.
data = load_data(10000)



def map(data, lat, lon, zoom):
    st.write(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state={
            "latitude": lat,
            "longitude": lon,
            "zoom": zoom,
            "pitch": 50,
        },
        layers=[
            pdk.Layer(
                "HexagonLayer",
                data=data,
                get_position=["lon", "lat"],
                radius=100,
                elevation_scale=4,
                elevation_range=[0, 1000],
                pickable=True,
                extruded=True,
            ),
        ]
    ))
def poi_map(data,poi,hour_selected,list_of_rows):
    #DATA is a dataframe
    #poi is a dict of the name and the tuple of locations

    # SETTING THE ZOOM LOCATIONS FOR THE AIRPORTS
    zoom_level = 12

    with list_of_rows[0]:
        st.write(list(poi.keys())[0])
        coords = (list(poi.values())[0][0],list(poi.values())[0][1])
        map(data, coords[0], coords[1], 12)

    with list_of_rows[1]:
        st.write(list(poi.keys())[1])
        coords = (list(poi.values())[1][0], list(poi.values())[1][1])
        map(data, coords[0], coords[1], 12)

    with list_of_rows[2]:
        st.write(list(poi.keys())[2])
        coords = (list(poi.values())[2][0],list(poi.values())[2][1])
        map(data, coords[0], coords[1], 12)
# LAYING OUT THE TOP SECTION OF THE APP

row1_1, row1_2 = st.beta_columns((2, 3))
row2_1, row2_2, row2_3, row2_4 = st.beta_columns((2,1,1,1))
poi={}
# LAYING OUT THE MIDDLE SECTION OF THE APP WITH THE MAPS
list_of_rows = [row2_2, row2_3, row2_4]
zoom_level = 12

with row1_1:
    st.title("NYC Uber Ridesharing Data")
    st.write("The below slider uses a 24hr clock. For example 23:00 is 11:00PM.")
    hour_selected = st.slider("Select hour of pickup", 0, 23)


with row1_2:
    st.write(
        """
        ##
        Examining how Uber pickups vary over time in New York City and looking at key high traffic areas. Take a look at
        the airports, famous landmarks, and event venues.
        By sliding the slider on the left you can view different slices of time and explore different transportation trends.
        """)
    selection = st.radio(label="Points of Interest", options=('Airports', 'Landmarks', 'Event Venues'))
    if selection == 'Airports':
        poi = {'**La Guardia Airport**': [40.7900, -73.8700],
               '**JFK Airport**': [40.6650, -73.7821],
               '**Newark Airport**': [40.7090, -74.1805]
               }
        poi_map(data=data, poi=poi, hour_selected=hour_selected, list_of_rows=list_of_rows)
    elif selection == 'Landmarks':
        poi = {'**Times Square**': [40.7580, -73.9855],
               '**Empire State Building**': [40.7484, -73.9857],
               '**Statue of Liberty**': [40.6892, -74.0445]
               }
        poi_map(data=data, poi=poi, hour_selected=hour_selected, list_of_rows=list_of_rows)

    elif selection == 'Event Venues':
        poi = {'**MSG**': [40.7505, -73.9934],
               '**RadioCity Music Hall**': [40.7600, -73.9800],
               '**Yankee Stadium**': [40.8296, -73.9262]
               }
        poi_map(data=data, poi=poi, hour_selected=hour_selected, list_of_rows=list_of_rows)


# FILTERING DATA BY HOUR SELECTED

data = data[data[DATE_COLUMN].dt.hour == hour_selected]

with row2_1:
    middle = "**All New York City from %i:00 and %i:00**" % (hour_selected, (hour_selected + 1) % 24)
    st.write(middle)
    map(data, np.average(data["lat"]), np.average(data["lon"]), 11)


#if st.checkbox('Tourist Areas'):
#if st.checkbox('Event Venues'):
# FILTERING DATA FOR THE HISTOGRAM
filtered = data[
    (data[DATE_COLUMN].dt.hour >= hour_selected) & (data[DATE_COLUMN].dt.hour < (hour_selected + 1))
    ]

hist = np.histogram(filtered[DATE_COLUMN].dt.minute, bins=60, range=(0, 60))[0]

chart_data = pd.DataFrame({"minute": range(60), "pickups": hist})

# LAYING OUT THE HISTOGRAM SECTION

st.write("")

st.write("**Breakdown of rides per minute between %i:00 and %i:00**" % (hour_selected, (hour_selected + 1) % 24))

st.altair_chart(alt.Chart(chart_data)
    .mark_area(
        interpolate='step-after',
    ).encode(
        x=alt.X("minute:Q", scale=alt.Scale(nice=False)),
        y=alt.Y("pickups:Q"),
        tooltip=['minute', 'pickups']
    ).configure_mark(
        opacity=0.5,
        color='red'
    ), use_container_width=True)

if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(data)