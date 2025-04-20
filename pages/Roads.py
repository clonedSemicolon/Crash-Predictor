import streamlit as st
import pandas as pd
import plotly.express as px
from utilities import load_crash_data_with_progress, preprocess_crash_data

st.set_page_config(page_title="Road Safety Insights", layout="wide")
st.title("🚦 Road Safety Condition Insights")

if 'combined_df' not in st.session_state:
    st.session_state['combined_df'] = preprocess_crash_data(load_crash_data_with_progress())

combined_df = st.session_state['combined_df']

st.sidebar.header("🔎 Filter Conditions")
selected_trafficway = st.sidebar.multiselect("Select Trafficway Type", options=combined_df['TRAFFICWAY_TYPE'].dropna().unique())
selected_surface = st.sidebar.multiselect("Select Surface Condition", options=combined_df['ROADWAY_SURFACE_COND'].dropna().unique())
selected_defect = st.sidebar.multiselect("Select Road Defects", options=combined_df['ROAD_DEFECT'].dropna().unique())

filtered_df = combined_df.copy()
if selected_trafficway:
    filtered_df = filtered_df[filtered_df['TRAFFICWAY_TYPE'].isin(selected_trafficway)]
if selected_surface:
    filtered_df = filtered_df[filtered_df['ROADWAY_SURFACE_COND'].isin(selected_surface)]
if selected_defect:
    filtered_df = filtered_df[filtered_df['ROAD_DEFECT'].isin(selected_defect)]

st.subheader("📊 Crash Count by Road Condition Factors")
grouped = filtered_df.groupby(['TRAFFICWAY_TYPE', 'ROADWAY_SURFACE_COND', 'ROAD_DEFECT'])['INJURIES_TOTAL'].agg(['count', 'mean']).reset_index()
grouped.rename(columns={'count': 'Crash Count', 'mean': 'Avg Injuries'}, inplace=True)

fig = px.bar(grouped, x='TRAFFICWAY_TYPE', y='Crash Count', color='ROADWAY_SURFACE_COND', barmode='group',
             facet_col='ROAD_DEFECT', text='Avg Injuries',
             title="Crash Frequency & Severity by Road Types, Surface Conditions & Defects",
             labels={'TRAFFICWAY_TYPE': 'Road Type', 'Crash Count': 'Number of Crashes'})
fig.update_layout(font=dict(color='white'), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(fig, use_container_width=True)

st.subheader("🔥 Injury Severity Heatmap")
pivot = grouped.pivot_table(index='TRAFFICWAY_TYPE', columns='ROADWAY_SURFACE_COND', values='Avg Injuries', aggfunc='mean')
fig2 = px.imshow(pivot, text_auto=True, aspect='auto', color_continuous_scale='Reds', labels={"color": "Avg Injuries"})
fig2.update_layout(title='Average Injury Severity by Road Type & Surface Condition',
                   xaxis_title='Surface Condition', yaxis_title='Trafficway Type',
                   font=dict(color='white'), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(fig2, use_container_width=True)

with st.expander("📄 Show Data Table"):
    st.dataframe(grouped)