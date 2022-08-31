import streamlit as st
import base64
import gzip
import json
import pandas as pd
import pydeck as pdk


geo_keys = {'latitude':'latitude', 'lat':'latitude', 'longitude':'longitude', 'lng':'longitude'}


st.title('AutoMapper')
if 'coords' not in st.session_state:
    st.session_state.coords = {}


def unbase64(data):
    try: return base64.b64decode(data)
    except: return data


def ungzip(data):
    try: return gzip.decompress(data)
    except: return data


def unjson(data):
    try: return json.loads(data)
    except: return data


def get_list(store, hierarchy_names, tag):
    tags = hierarchy_names[:-1] if type(hierarchy_names[-1]) == int else hierarchy_names
    parent_name = '.'.join([str(t) for t in tags])
    if not parent_name in store:
        store[parent_name] = {'latitude':[], 'longitude':[]}
    node = store[parent_name]
    return node[tag]


def deep_pluck(store, hierarchy_names, node):
    '''Converts anything lat/lng into a datastructure like so:
       
      {
          "waypoint.0.shapes": {
            "lat": [1.1, 2.2, 3.3],
            "lng": [4.4, 5.5, 6.6]
          },...
      }
    '''
    if type(node) == dict:
        for key,value in node.items():
            if type(value) == float and key in geo_keys:
                l = get_list(store, hierarchy_names, geo_keys[key])
                l.append(value)
            else:
                deep_pluck(store, hierarchy_names+[key], value)
    elif type(node) == list:
        for i,value in enumerate(node):
            deep_pluck(store, hierarchy_names+[i], value)
    # ignore strings and ints
    return store


def uncoord(data):
    return deep_pluck(store={}, hierarchy_names=[], node=data)



def unpack_data(data):
    data = unbase64(data.strip())
    data = ungzip(data)
    data = unjson(data)
    data = uncoord(data)
    return data


def update_buttons():
    data = unpack_data(st.session_state.text)
    st.session_state.coords = data
    st.session_state.text = ''


with st.form(key='input_coord_data'):
    st.text_area('Paste geocoords', key='text')
    submit = st.form_submit_button(label='Parse', on_click=update_buttons)

for label,coords in st.session_state.coords.items():
    if st.button(label):
        df = pd.DataFrame(coords)
        st.map(df)
