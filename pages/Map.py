import streamlit as st
from utilities import load_large_html_map
import streamlit.components.v1 as components

st.title("Crash Map")

if 'map_html' not in st.session_state:
    with st.spinner("Preloading interactive map..."):
        st.session_state['map_html'] = load_large_html_map()

# Render the map
if 'map_html' in st.session_state:
    components.html(st.session_state['map_html'], height=700)
else:
    st.info("Map is still loading. Please wait...")