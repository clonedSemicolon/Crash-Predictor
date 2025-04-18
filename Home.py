import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import streamlit.components.v1 as components
from utilities import extract_damage_value, load_crash_data, preprocess_crash_data, filter_data, load_map_html
import plotly.express as px

st.set_page_config(page_title="Chicago Crash Dashboard", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS
st.markdown("""
<style>
    body {
        color: #fff;
        background-color: #0e1117;
        padding: 0;
    }
    .stApp {
        max-width: 100%;
        margin: 0 auto;
    }
    .metric-card {
        background-color: #1c1f26;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #4cc9f0;
    }
    .metric-label {
        font-size: 1rem;
        color: #a0aec0;
    }
</style>
""", unsafe_allow_html=True)

st.title("Chicago Crash Dashboard")

if 'combined_df' not in st.session_state:
    st.session_state['combined_df'] = preprocess_crash_data(load_crash_data())

combined_df = st.session_state['combined_df']

# Sidebar Filters
st.sidebar.header("Filter Data")
start_date = st.sidebar.date_input("Start Date", pd.to_datetime('2020-01-01'))
end_date = st.sidebar.date_input("End Date", pd.to_datetime('2025-01-01'))
weather_condition = st.sidebar.selectbox("Select Weather Condition", ['All'] + list(combined_df['WEATHER_CONDITION'].dropna().unique()))
severity = st.sidebar.selectbox("Select Crash Severity", ['All', 'Minor', 'Moderate', 'Severe'])

filtered_df = filter_data(combined_df, start_date, end_date, weather_condition, severity)
st.session_state['filtered_df'] = filtered_df

# Metrics
col1, col2, col3 = st.columns([2, 3, 3])
with col1:
    st.markdown("### Key Metrics")
    total_crashes = len(filtered_df)
    total_injuries = filtered_df['INJURIES_TOTAL'].sum()
    avg_speed_limit = filtered_df['POSTED_SPEED_LIMIT'].mean()
    total_damage = filtered_df['DAMAGE'].sum()

    metrics = [
        ("Total Crashes", f"{total_crashes:,}"),
        ("Total Injuries", f"{total_injuries:,}"),
        ("Avg Speed Limit", f"{avg_speed_limit:.1f} mph"),
        ("Total Damage Cost", f"${total_damage}")
    ]
    for label, value in metrics:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{value}</div>
            <div class="metric-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)
        st.write("")

# Crash Severity Pie
with col2:
    st.markdown("### Crash Severity Breakdown")
    fig = go.Figure(data=[go.Pie(labels=['No Injuries', 'Injuries'],
                                 values=[(filtered_df['INJURIES_TOTAL']==0).sum(), (filtered_df['INJURIES_TOTAL']>0).sum()],
                                 hole=.3,
                                 marker_colors=['#4cc9f0', '#f72585'])])
    fig.update_layout(title_text="Crashes with Injuries vs No Injuries", legend_orientation="h", legend=dict(x=0.5, xanchor="center"),
                      plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
    st.plotly_chart(fig, use_container_width=True)

# Damage Cost Bar
with col3:
    st.markdown("### Economic Impact")
    damage_summary = filtered_df.groupby('DAMAGE_CATEGORY')['DAMAGE_VALUE'].sum().sort_values(ascending=True)
    fig = go.Figure(go.Bar(x=damage_summary.values, y=damage_summary.index, orientation='h', marker_color='#4cc9f0'))
    fig.update_layout(title='Damage Cost by Category', xaxis_title='Total Damage Cost ($)', yaxis_title='Damage Category',
                      font=dict(color='white'), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)


    

# Crash Map
st.markdown("### Crash Hotspot Map")
html_data = load_map_html()
components.html(html_data, height=700, scrolling=False)


st.markdown("### Time-based Analysis")

col4, col5 = st.columns(2)

with col4:
    st.markdown("#### Crashes by Hour")
    if 'CRASH_HOUR' in filtered_df.columns:
        hour_counts = filtered_df['CRASH_HOUR'].value_counts().sort_index()
        all_hours = pd.Series(range(24))
        hour_counts = hour_counts.reindex(all_hours, fill_value=0)

        fig = go.Figure(data=[go.Bar(x=hour_counts.index, y=hour_counts.values, marker_color='#4cc9f0')])
        fig.update_layout(
            title='Crashes by Hour of Day',
            xaxis_title='Hour',
            yaxis_title='Number of Crashes',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis=dict(tickmode='array', tickvals=list(range(0, 24, 4)), ticktext=[f'{i:02d}:00' for i in range(0, 24, 4)]),
        )
        st.plotly_chart(fig, use_container_width=True)

with col5:
    st.markdown("#### Crashes by Month")
    if 'CRASH_MONTH' in filtered_df.columns:
        month_counts = filtered_df['CRASH_MONTH'].value_counts().sort_index()
        all_months = pd.Series(range(1, 13))
        month_counts = month_counts.reindex(all_months, fill_value=0)
        
        fig = go.Figure(data=[go.Bar(x=month_counts.index, y=month_counts.values, marker_color='#4cc9f0')])
        fig.update_layout(
            title='Crashes by Month',
            xaxis_title='Month',
            yaxis_title='Number of Crashes',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis=dict(tickmode='array', tickvals=list(range(1, 13)), ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']),
        )
        st.plotly_chart(fig, use_container_width=True)

# Weather and Lighting Condition Breakdown
st.markdown("### Weather and Lighting Conditions")

col6, col7 = st.columns(2)

with col6:
    st.markdown("#### Weather Condition Breakdown")
    weather_counts = filtered_df['WEATHER_CONDITION'].value_counts()
    fig_weather = go.Figure(go.Bar(x=weather_counts.index, y=weather_counts.values, marker_color='#7209b7'))
    fig_weather.update_layout(title='Crashes by Weather Condition', xaxis_title='Weather', yaxis_title='Crashes', font=dict(color='white'),
    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_weather, use_container_width=True)

with col7:
    st.markdown("#### Lighting Condition Breakdown")
    light_counts = filtered_df['LIGHTING_CONDITION'].value_counts()
    fig_light = go.Figure(go.Pie(labels=light_counts.index, values=light_counts.values, marker_colors=['#560bad','#f72585','#4cc9f0']))
    fig_light.update_layout(title='Lighting Conditions During Crashes', font=dict(color='white'),
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_light, use_container_width=True)
